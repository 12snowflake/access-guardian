from datetime import date, timedelta
from models import session, Account
from checker import calculate_risk

# Clear out old data first, so re-running this file doesn't create duplicates
session.query(Account).delete()
session.commit()

today = date.today()

seed_accounts = [
    Account(
        name="Rahul Mehta", org="ByteSecure IT Services", role="DB Admin",
        access_level="Privileged",
        contract_start=today - timedelta(days=200),
        contract_end=today - timedelta(days=5),      # expired 5 days ago
        status="active",
        login_behaviour="Unusual",
    ),
    Account(
        name="Priya Nair", org="CloudVendor Corp", role="Network Engineer",
        access_level="Privileged",
        contract_start=today - timedelta(days=100),
        contract_end=today + timedelta(days=2),       # expiring in 2 days
        status="active",
        login_behaviour="Normal",
    ),
    Account(
        name="Amit Shah", org="SecureAudit LLP", role="Auditor",
        access_level="Standard",
        contract_start=today - timedelta(days=50),
        contract_end=today + timedelta(days=60),      # safely active
        status="active",
        login_behaviour="Normal",
    ),
    Account(
        name="Sneha Rao", org="ByteSecure IT Services", role="System Admin",
        access_level="Privileged",
        contract_start=today - timedelta(days=400),
        contract_end=today - timedelta(days=100),     # expired 100 days ago!
        status="active",                                 # ⚠️ still marked active — the danger case
        login_behaviour="Suspicious",
    ),
]

for acc in seed_accounts:
    calculate_risk(acc)

session.add_all(seed_accounts)
session.commit()

print(f"Seeded {len(seed_accounts)} accounts into the database ✅")