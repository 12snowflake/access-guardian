import os
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# Database path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "access_guardian.db")

engine = create_engine(f"sqlite:///{DB_PATH}")

Base = declarative_base()


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)

    # User details
    name = Column(String)
    org = Column(String)
    role = Column(String)

    # Access details
    access_level = Column(String)
    contract_start = Column(Date)
    contract_end = Column(Date)

    # Status
    status = Column(String, default="active")
    last_checked = Column(DateTime, nullable=True)

    # NEW FIELDS
    risk_score = Column(Integer, default=0)
    risk_level = Column(String, default="Low")

    # NEWEST FIELDS (dashboard v2)
    risk_reasons = Column(String, default="")          # pipe-separated list of "why" the score is what it is
    security_actions = Column(String, default="")      # pipe-separated list of actions taken on this account
    ai_recommendation = Column(String, default="")      # short recommended next step
    login_behaviour = Column(String, default="Normal")  # Normal / Unusual / Suspicious
    business_impact = Column(String, default="")        # human-readable impact-if-compromised note


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True)

    account_name = Column(String)
    org = Column(String)

    event_type = Column(String)
    details = Column(String)

    timestamp = Column(DateTime, default=datetime.now)


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


if __name__ == "__main__":
    print("Database created successfully.")