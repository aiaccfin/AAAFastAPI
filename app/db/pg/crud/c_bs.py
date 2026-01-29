from fastapi import HTTPException, status
from sqlmodel import Session, select
from app.db.pg.model import m_bs
from app.db.pg.model.m_bs_ai import BankStatementAI
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_all(db: Session = None):
    all = db.exec(select(m_bs.BSDetail)).all()
    logger.info(f"Retrieved all bank statement details: {all}")
    return all

def get_all_summary(db: Session = None):
    all = db.exec(select(m_bs.BSSummary)).all()
    logger.info(f"Retrieved all bank statement summaries: {all}")   
    return all


def get_one(one_id: int, db: Session = None):
    one_bs_detail = db.get(m_bs.BSDetail, one_id)
    if not one_bs_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"bs_detail not found with id: {one_id}",
        )
    return one_bs_detail

def get_one_detail_based_on_summary(one_id: int, db: Session = None):
    statement = select(m_bs.BSDetail).where(m_bs.BSDetail.summary_id == one_id)
    results = db.exec(statement).all()
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"bs_detail not found with id: {one_id}",
        )
    return results

def get_one_detail_based_on_summary_uuid(uuid_string: str, db: Session = None):
    statement = select(m_bs.BSDetail).where(m_bs.BSDetail.uuid_string == uuid_string)
    results = db.exec(statement).all()
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"bs_detail not found with uuid: {uuid_string}",
        )
    return results


def get_one_summary(one_id: int, db: Session = None):
    one_bs_sum = db.get(m_bs.BSSummary, one_id)
    if not one_bs_sum:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"bs_summary not found with id: {one_id}",
        )
    return one_bs_sum


def get_one_summary_uuid(uuid_string: str, db: Session = None):
    one_bs_sum = db.query(m_bs.BSSummary).filter(m_bs.BSSummary.uuid_string == uuid_string).first()
    if not one_bs_sum:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"bs_summary not found with uuid: {uuid_string}",
        )
    return one_bs_sum


def create_bs_detail(bs_detail: m_bs.BSDetailCreate, db: Session = None):
    bs_detail_to_db = m_bs.BSDetail.model_validate(bs_detail)
    db.add(bs_detail_to_db)
    db.commit()
    db.refresh(bs_detail_to_db)
    return bs_detail_to_db




def update_bs_detail(one_id: int, bs_detail: m_bs.BSDetailUpdate, db: Session = None):
    bs_detail_to_update = db.get(m_bs.BSDetail, one_id)
    if not bs_detail_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"bs_detail not found with id: {one_id}",
        )

    # if bs_detail.BSDetail_note is not None:
    #         bs_detail_to_update.BSDetail_note = bs_detail.BSDetail_note

    for field, value in bs_detail.model_dump(exclude_unset=True).items():
            setattr(bs_detail_to_update, field, value)

    db.add(bs_detail_to_update)
    db.commit()
    db.refresh(bs_detail_to_update)
    return bs_detail_to_update


def delete_bs_detail(one_id: int, db: Session = None):
    bs_detail  = db.get(m_bs.BSDetail, one_id)
    if not bs_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"bs_detail not found with id: {one_id}",
        )

    db.delete(bs_detail)
    db.commit()
    return {"ok": True}


    
    
# def create_bs_from_upload(bs_data: m_bs.BSSummaryCreate, db: Session):
#     try:
#         # Create summary
#         db_summary = m_bs.BSSummary(**bs_data.dict(exclude={"transactions"}))
#         db.add(db_summary)
#         db.commit()
#         db.refresh(db_summary)

#         # Create details
#         for transaction in bs_data.transactions:
#             db_detail = m_bs.BSDetail(
#                 **transaction.dict(),
#                 summary_id=db_summary.id
#             )
#             db.add(db_detail)
        
#         db.commit()

#         return {
#             "summary_id": db_summary.id,
#             "transaction_count": len(bs_data.transactions)
#         }

#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=500,
#             detail=f"Unexpected error: {str(e)}"
#         )


def create_bs_from_upload(ai_data: BankStatementAI, db: Session):
    try:
        # 1. Save SUMMARY (BSSummary)
        summary_data = ai_data.summary.dict()  # Extract only summary fields
        db_summary = m_bs.BSSummary(**summary_data)
        db.add(db_summary)
        db.commit()
        db.refresh(db_summary)

        # 2. Save DETAILS (BSDetail)
        transaction_count = 0
        for transaction in ai_data.transactions:  # Access transactions from AI data
            detail_data = transaction.dict()
            detail_data["summary_id"] = db_summary.id  # Link to parent
            
            db_detail = m_bs.BSDetail(**detail_data)
            db.add(db_detail)
            transaction_count += 1
        
        db.commit()

        return {
            "summary_id": db_summary.id,
            "transaction_count": transaction_count
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Database error: {str(e)}")
    



def save_parsed_bs_uuid(parsed_json: dict, uuid_name:str, db: Session) -> m_bs.BSSummary:
    # Step 1: Create BSSummary from parsed_json["summary"]
    summary_data = parsed_json["summary"]
    
    summary = m_bs.BSSummary(
        currency2=summary_data["statement_type"],
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
        updated_at=datetime.utcnow().isoformat(),
        biz_id = 888,
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


def get_details_by_summary_id(summary_id: int, db: Session = None):
    """Get all BSDetail records with the given summary_id."""
    statement = select(m_bs.BSDetail).where(m_bs.BSDetail.summary_id == summary_id)
    results = db.exec(statement).all()
    return results


def save_parsed_bs(parsed_json: dict, db: Session) -> m_bs.BSSummary:
    # Step 1: Create BSSummary from parsed_json["summary"]
    summary_data = parsed_json["summary"]
    
    summary = m_bs.BSSummary(
        currency2=summary_data["statement_type"],
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

    logger.info(f"1. Saving summary: {summary}")    
    db.add(summary)
    logger.info(f"2. Saving summary: {summary}")    
    db.commit()
    db.refresh(summary)
    logger.info(f"3. Summary saved: {summary}")

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
        logger.info(f"42. Saving summary: {summary.bank_name}")    

    db.commit()

    return summary


def save_bs_w_filename(parsed_json: dict, filename_uuid: str, db: Session) -> m_bs.BSSummary:
    # Step 1: Create BSSummary from parsed_json["summary"]
    logger.info(f"0. Saving summary: {summary}")    
    summary_data = parsed_json["summary"]
    
    summary = m_bs.BSSummary(
        uuid = filename_uuid,
        uuid_string = filename_uuid,
        currency2=summary_data["statement_type"],
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

    logger.info(f"1. Saving summary: {summary}")    
    db.add(summary)
    logger.info(f"2. Saving summary: {summary}")    
    db.commit()
    db.refresh(summary)
    logger.info(f"3. Summary saved: {summary}")

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
        logger.info(f"42. Saving summary: {summary.bank_name}")    

    db.commit()

    return summary
