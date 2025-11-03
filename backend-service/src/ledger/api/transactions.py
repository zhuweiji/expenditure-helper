from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.database import get_db_session

from ..api.entries import Entry, EntryCreate
from ..models.entry import Entry as EntryModel
from ..models.transaction import Transaction as TransactionModel


class TransactionBase(BaseModel):
    description: str
    transaction_date: datetime
    reference: Optional[str] = None


class TransactionCreate(TransactionBase):
    user_id: int
    entries: List[EntryCreate] = []


class TransactionUpdate(TransactionBase):
    entries: Optional[List[EntryCreate]] = None


class Transaction(TransactionBase):
    id: int
    user_id: int
    entries: List[Entry] = []

    class Config:
        from_attributes = True


router = APIRouter()


@router.post("/")
def create_transaction(
    transaction: TransactionCreate, db: Session = Depends(get_db_session)
):
    db_transaction = TransactionModel(
        user_id=transaction.user_id,
        description=transaction.description,
        transaction_date=transaction.transaction_date,
        reference=transaction.reference,
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    # Add entries if provided
    for entry in transaction.entries:
        db_entry = EntryModel(
            transaction_id=db_transaction.id,
            account_id=entry.account_id,
            amount=entry.amount,
            entry_type=entry.entry_type,
            description=entry.description,
        )
        db.add(db_entry)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.get("/")
def list_transactions(user_id: int, db: Session = Depends(get_db_session)):
    transactions = db.query(TransactionModel).filter(
        TransactionModel.user_id == user_id
    )
    return transactions.all()


@router.get("/{transaction_id}")
def read_transaction(
    transaction_id: int, user_id: int, db: Session = Depends(get_db_session)
):
    db_tx = (
        db.query(TransactionModel)
        .filter(
            TransactionModel.id == transaction_id, TransactionModel.user_id == user_id
        )
        .first()
    )
    if db_tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_tx


@router.put("/{transaction_id}")
def update_transaction(
    transaction_id: int,
    user_id: int,
    transaction: TransactionUpdate,
    db: Session = Depends(get_db_session),
):
    db_tx = (
        db.query(TransactionModel)
        .filter(
            TransactionModel.id == transaction_id, TransactionModel.user_id == user_id
        )
        .first()
    )
    if db_tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    setattr(db_tx, "description", transaction.description)
    setattr(db_tx, "transaction_date", transaction.transaction_date)
    setattr(db_tx, "reference", transaction.reference)

    # Optionally update entries
    if transaction.entries is not None:
        # Remove old entries
        db.query(EntryModel).filter(EntryModel.transaction_id == db_tx.id).delete()
        # Add new entries
        for entry in transaction.entries:
            db_entry = EntryModel(
                transaction_id=db_tx.id,
                account_id=entry.account_id,
                amount=entry.amount,
                entry_type=entry.entry_type,
                description=entry.description,
            )
            db.add(db_entry)
    db.commit()
    db.refresh(db_tx)
    return db_tx


@router.delete("/transactions/{transaction_id}")
def delete_transaction(
    transaction_id: int, user_id: int, db: Session = Depends(get_db_session)
):
    db_tx = (
        db.query(TransactionModel)
        .filter(
            TransactionModel.id == transaction_id, TransactionModel.user_id == user_id
        )
        .first()
    )
    if db_tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(db_tx)
    db.commit()
    return {"detail": "Transaction deleted"}
