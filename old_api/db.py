from sqlmodel import Session, select
from app.db.pg.model import m_bs
from app.db.pg.model.m_bs_ai import BankStatementAI
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def save_parsed_bs_uuid(parsed_json: dict, uuid_name:str, db: Session) -> m_bs.BSSummary:
    # Step 1: Create BSSummary from parsed_json["summary"]
    summary_data = parsed_json["summary"]
    
    summary = m_bs.BSSummary(
        uuid = uuid_name,
        uuid_string = uuid_name,
        account_number=summary_data["account_number"],
        account_name=summary_data["account_name"],
        bank_name=summary_data["bank_name"],
        period_start=datetime.strptime(summary_data["statement_period_start"], "%Y-%m-%d").date(),
        period_end=datetime.strptime(summary_data["statement_period_end"], "%Y-%m-%d").date(),
        opening_balance=summary_data["opening_balance"],
        closing_balance=summary_data["closing_balance"],
        currency=summary_data.get("currency", "USD"),
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat()
    )
    
    db.add(summary)
    db.commit()
    db.refresh(summary)

    # Step 2: Create BSDetail entries
    for tx in parsed_json["transactions"]:
        detail = m_bs.BSDetail(
            uuid = summary.uuid,
            uuid_string = summary.uuid_string,
            summary_id=summary.id,
            transaction_date=datetime.strptime(tx["date"], "%Y-%m-%d").date(),
            description=tx["description"],
            amount=tx["amount"],
            transaction_type=tx["transaction_type"],
            reference=tx.get("reference"),
            balance_after=tx.get("balance_after", 0.0),
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )
        db.add(detail)

    db.commit()

    return summary



def save_parsed_bs(parsed_json: dict, db: Session) -> m_bs.BSSummary:
    # Step 1: Create BSSummary from parsed_json["summary"]
    summary_data = parsed_json["summary"]
    
    summary = m_bs.BSSummary(
        account_number=summary_data["account_number"],
        account_name=summary_data["account_name"],
        bank_name=summary_data["bank_name"],
        period_start=datetime.strptime(summary_data["statement_period_start"], "%Y-%m-%d").date(),
        period_end=datetime.strptime(summary_data["statement_period_end"], "%Y-%m-%d").date(),
        opening_balance=summary_data["opening_balance"],
        closing_balance=summary_data["closing_balance"],
        currency=summary_data.get("currency", "USD"),
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat()
    )
    
    db.add(summary)
    db.commit()
    db.refresh(summary)

    # Step 2: Create BSDetail entries
    for tx in parsed_json["transactions"]:
        detail = m_bs.BSDetail(
            summary_id=summary.id,
            transaction_date=datetime.strptime(tx["date"], "%Y-%m-%d").date(),
            description=tx["description"],
            amount=tx["amount"],
            transaction_type=tx["transaction_type"],
            reference=tx.get("reference"),
            balance_after=tx.get("balance_after", 0.0),
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )
        db.add(detail)

    db.commit()

    return summary
