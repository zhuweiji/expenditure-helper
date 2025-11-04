from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.common.logger import get_logger
from src.database import get_db_session

from ..models.user import User

log = get_logger(__name__)

router = APIRouter()


@router.get("/{user_id}/accounts")
def get_user_accounts(user_id: int, db: Session = Depends(get_db_session)):
    """
    Get all accounts for a user, grouped by type, with credit and debit totals.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    log.info(f"Fetching accounts for user_id: {user_id}")

    accounts_by_type = {}
    for account in user.accounts:
        account_type = account.account_type or "unspecified"

        if account_type not in accounts_by_type:
            accounts_by_type[account_type] = []

        # Calculate credit and debit totals for this account
        credit_total = sum(
            entry.amount for entry in account.entries if entry.entry_type == "credit"
        )
        debit_total = sum(
            entry.amount for entry in account.entries if entry.entry_type == "debit"
        )

        log.info(
            entry.amount for entry in account.entries if entry.entry_type == "debit"
        )

        accounts_by_type[account_type].append(
            {
                "account_id": account.id,
                "account_name": account.name,
                "credit_total": float(credit_total),
                "debit_total": float(debit_total),
                "balance": float(debit_total - credit_total),
            }
        )

    return {
        "user_id": user.id,
        "username": user.username,
        "accounts_by_type": accounts_by_type,
    }


@router.get("/{user_id}/stats")
def get_user_stats(user_id: int, db: Session = Depends(get_db_session)):
    """
    Get statistics for a user including account counts and transaction counts.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user.id,
        "username": user.username,
        "total_accounts": len(user.accounts),
        "total_transactions": len(user.transactions),
        "total_statements": len(user.statements),
        "accounts_by_type": _count_accounts_by_type(user.accounts),
    }


def _count_accounts_by_type(accounts):
    """Helper function to count accounts by type"""
    counts = {}
    for account in accounts:
        account_type = account.account_type or "unspecified"
        counts[account_type] = counts.get(account_type, 0) + 1
    return counts
