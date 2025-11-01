from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from ..models.account import Account
from ..schemas.account import AccountCreate, AccountUpdate
from ..database import get_db

router = APIRouter()

@router.post("/accounts/", response_model=Account)
def create_account(account: AccountCreate, db: Session = next(get_db())):
    db_account = Account(name=account.name, balance=account.balance)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@router.get("/accounts/{account_id}", response_model=Account)
def read_account(account_id: int, db: Session = next(get_db())):
    account = db.query(Account).filter(Account.id == account_id).first()
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@router.put("/accounts/{account_id}", response_model=Account)
def update_account(account_id: int, account: AccountUpdate, db: Session = next(get_db())):
    db_account = db.query(Account).filter(Account.id == account_id).first()
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    db_account.name = account.name
    db_account.balance = account.balance
    db.commit()
    db.refresh(db_account)
    return db_account

@router.delete("/accounts/{account_id}", response_model=Account)
def delete_account(account_id: int, db: Session = next(get_db())):
    db_account = db.query(Account).filter(Account.id == account_id).first()
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(db_account)
    db.commit()
    return db_account