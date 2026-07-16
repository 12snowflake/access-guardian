from datetime import date, datetime
from models import session, Account, AuditLog


BUSINESS_IMPACT_BY_ROLE = {
    "DB Admin": "Full database access — a compromise could expose or corrupt all stored records.",
    "System Admin": "Root/system-level access — a compromise could take down critical infrastructure.",
    "Network Engineer": "Access to network configuration — a compromise could reroute or intercept traffic.",
    "Auditor": "Read access to audit trails — a compromise could hide evidence of other attacks.",
}


def calculate_risk(account):
    """
    Calculates a risk score for an account, and explains *why*
    (reasons), what was *done about it* (actions), and what the
    AI engine *recommends next*.
    """

    risk = 0
    reasons = []
    actions = []

    # Privileged accounts are inherently riskier
    if account.access_level == "Privileged":
        risk += 20
        reasons.append("Privileged access level (+20)")

    # Contract expired
    days_expired = (date.today() - account.contract_end).days
    if account.contract_end < date.today():
        risk += 50
        reasons.append(f"Contract expired {days_expired} day(s) ago (+50)")
    elif (account.contract_end - date.today()).days <= 3:
        reasons.append("Contract expiring within 3 days")

    # Already revoked
    if account.status == "revoked":
        risk += 10
        reasons.append("Account status is revoked (+10)")
        actions.append("Access auto-revoked")
    else:
        actions.append("Access currently active")

    # Suspicious login behaviour bumps risk too
    if account.login_behaviour == "Suspicious":
        risk += 15
        reasons.append("Suspicious login behaviour detected (+15)")
        actions.append("Flagged for security review")
    elif account.login_behaviour == "Unusual":
        risk += 5
        reasons.append("Unusual login pattern (+5)")

    if not reasons:
        reasons.append("No risk factors detected")

    account.risk_score = min(risk, 100)

    if account.risk_score >= 80:
        account.risk_level = "Critical"
    elif account.risk_score >= 60:
        account.risk_level = "High"
    elif account.risk_score >= 30:
        account.risk_level = "Medium"
    else:
        account.risk_level = "Low"

    # --- AI recommendation (simple rule-based "engine") ---
    if account.risk_level == "Critical":
        account.ai_recommendation = "Revoke immediately and force credential rotation."
    elif account.risk_level == "High":
        account.ai_recommendation = "Review access now and shorten contract renewal window."
    elif account.risk_level == "Medium":
        account.ai_recommendation = "Monitor closely; confirm contract renewal status."
    else:
        account.ai_recommendation = "No action needed; continue routine monitoring."

    account.risk_reasons = " | ".join(reasons)
    account.security_actions = " | ".join(actions) if actions else "No action taken"
    account.business_impact = BUSINESS_IMPACT_BY_ROLE.get(
        account.role, "Standard access — limited blast radius if compromised."
    )


def check_expired_access():
    today = date.today()

    accounts = session.query(Account).all()

    revoked_this_run = []

    for account in accounts:

        calculate_risk(account)

        if account.status == "active" and account.contract_end < today:

            account.status = "revoked"
            account.last_checked = datetime.now()

            calculate_risk(account)

            revoked_this_run.append(account)

            log_entry = AuditLog(
                account_name=account.name,
                org=account.org,
                event_type="auto_revoke",
                details=f"Access auto-revoked. Contract ended on {account.contract_end}.",
                timestamp=datetime.now()
            )

            session.add(log_entry)

        else:
            account.last_checked = datetime.now()

    session.commit()

    return revoked_this_run


def simulate_suspicious_access_attempt(account_name):

    account = session.query(Account).filter(Account.name == account_name).first()

    if not account:
        print(f"No account found for {account_name}")
        return

    if account.status == "revoked":

        account.login_behaviour = "Suspicious"
        calculate_risk(account)
        account.risk_score = min(account.risk_score + 20, 100)
        account.risk_level = "Critical"
        account.security_actions += " | Login attempt blocked & flagged"

        log_entry = AuditLog(
            account_name=account.name,
            org=account.org,
            event_type="suspicious_attempt",
            details="Access attempt on a REVOKED account. Possible insider threat.",
            timestamp=datetime.now()
        )

        session.add(log_entry)
        session.commit()

        print(
            f"🚨 FLAGGED: Access attempt detected on revoked account — {account.name} ({account.org})"
        )

    else:
        print(f"{account.name}'s account is still active — no flag raised.")


if __name__ == "__main__":

    revoked = check_expired_access()

    if revoked:

        print(f"\n⚠️ Revoked {len(revoked)} expired account(s):")

        for acc in revoked:

            print(
                f" - {acc.name} ({acc.org}) | Risk Score: {acc.risk_score} | {acc.risk_level}"
            )

    else:
        print("✅ No expired accounts found.")

    print("\n--- Simulating Suspicious Access Attempt ---")

    simulate_suspicious_access_attempt("Sneha Rao")