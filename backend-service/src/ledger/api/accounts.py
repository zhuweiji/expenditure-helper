from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from src.database import get_db_session

from ..models.account import Account

router = APIRouter()


class AccountBaseRequest(BaseModel):
    name: str
    balance: int


class AccountCreateRequest(AccountBaseRequest):
    user_id: int


class AccountUpdateRequest(AccountBaseRequest):
    pass


class AccountRequest(AccountBaseRequest):
    id: int
    user_id: int

    class Config:
        from_attributes = True


@router.post("/")
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


@router.get("/")
def list_accounts(user_id: int, db: Session = Depends(get_db_session)):
    accounts = db.query(Account).filter(Account.user_id == user_id)
    return accounts.all()


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
