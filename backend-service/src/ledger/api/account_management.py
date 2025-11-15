from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from src.common.logger import get_logger
from src.database import get_db_session

from ..models.account import Account
from ..models.transaction import Transaction
from .account_schemas import AccountCreateRequest, AccountUpdateRequest

log = get_logger(__name__)

router = APIRouter()


@router.post("")
def create_account(
    account: AccountCreateRequest, db: Session = Depends(get_db_session)
):
    db_account = Account(
        name=account.name, balance=account.balance, user_id=account.user_id
    )
    db.add(db_account)
    try:
        db.commit()
        db.refresh(db_account)
        return db_account
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="An account with this name already exists for this user",
        )


@router.get("/{account_id}")
def read_account(account_id: int, user_id: int, db: Session = Depends(get_db_session)):
    account = (
        db.query(Account)
        .filter(Account.id == account_id, Account.user_id == user_id)
        .first()
    )
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.put("/{account_id}")
def update_account(
    account_id: int,
    user_id: int,
    account: AccountUpdateRequest,
    db: Session = Depends(get_db_session),
):
    db_account = (
        db.query(Account)
        .filter(Account.id == account_id, Account.user_id == user_id)
        .first()
    )
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    db_account.name = account.name
    db_account.balance = account.balance  # type: ignore

    db.commit()
    db.refresh(db_account)
    return db_account


@router.delete("/{account_id}")
def delete_account(
    account_id: int, user_id: int, db: Session = Depends(get_db_session)
):
    db_account = (
        db.query(Account)
        .filter(Account.id == account_id, Account.user_id == user_id)
        .first()
    )
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(db_account)
    db.commit()
    return db_account


@router.delete("/user/{user_id}/clear")
def clear_all_accounts(user_id: int, db: Session = Depends(get_db_session)):
    """Clear all transactions from all accounts for a specific user"""
    # Get all transactions owned by the user
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    deleted_count = len(transactions)

    # Delete each transaction individually to trigger cascade deletes for entries
    for transaction in transactions:
        db.delete(transaction)

    db.commit()

    log.info(
        f"Cleared {deleted_count} transaction(s) (and associated entries) for user {user_id}"
    )
    return {
        "deleted_count": deleted_count,
        "message": f"Cleared {deleted_count} transaction(s) and all associated entries for user {user_id}",
    }
