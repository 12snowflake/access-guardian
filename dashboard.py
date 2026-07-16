import pandas as pd
from models import session, Account, AuditLog

def show_dashboard():
    accounts = session.query(Account).all()

    # Convert the database rows into a list of dictionaries,
    # which pandas can turn into a nice table
    data = []
    for acc in accounts:
        data.append({
            "Name": acc.name,
            "Organization": acc.org,
            "Role": acc.role,
            "Access Level": acc.access_level,
            "Contract End": acc.contract_end,
            "Status": acc.status,
            "Last Checked": acc.last_checked
        })

    df = pd.DataFrame(data)
    return df

def show_audit_log():
    logs = session.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()

    data = []
    for log in logs:
        data.append({
            "Timestamp": log.timestamp,
            "Account": log.account_name,
            "Organization": log.org,
            "Event Type": log.event_type,
            "Details": log.details
        })

    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    df = show_dashboard()
    print("\n=== ACCESS GUARDIAN — Account Status Dashboard ===\n")
    print(df.to_string(index=False))

    log_df = show_audit_log()
    print("\n=== AUDIT LOG — Security Event History ===\n")
    print(log_df.to_string(index=False))
    