from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db_session

from ..models.account import Account
from ..models.entry import Entry as EntryModel
from ..models.transaction import Transaction as TransactionModel
from .transactions_schemas import (
    PaginatedTransactionResponse,
    Transaction,
    TransactionCreate,
    TransactionUpdate,
)

router = APIRouter()


def _create_transaction_with_entries(
    transaction: TransactionCreate, db: Session
) -> TransactionModel:
    """
    Internal method to create a transaction with its associated entries.

    Args:
        transaction: TransactionCreate schema with user_id, description, date, reference, and entries
        db: Database session

    Returns:
        The created TransactionModel instance
    """
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
            timestamp=entry.timestamp if entry.timestamp else datetime.utcnow(),
        )
        db.add(db_entry)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.post("")
def create_transaction(
    transaction: TransactionCreate, db: Session = Depends(get_db_session)
):
    """Create a single transaction with its entries."""
    return _create_transaction_with_entries(transaction, db)


@router.post("/batch")
def batch_create_transactions(
    transactions: List[TransactionCreate], db: Session = Depends(get_db_session)
):
    """
    Create multiple transactions in batch.

    Args:
        transactions: List of TransactionCreate schemas
        db: Database session

    Returns:
        List of created transactions
    """
    created_transactions = []
    for transaction in transactions:
        db_transaction = _create_transaction_with_entries(transaction, db)
        created_transactions.append(db_transaction)
    return created_transactions


@router.get("")
def list_transactions(
    user_id: int,
    startDate: Optional[str] = None,
    endDate: Optional[str] = None,
    page: int = 1,
    page_size: int = 1000,
    db: Session = Depends(get_db_session),
):
    # Build query with filters
    query = db.query(TransactionModel).filter(TransactionModel.user_id == user_id)

    # Apply date filters if provided
    if startDate:
        start_datetime = datetime.fromisoformat(startDate.replace("Z", "+00:00"))
        query = query.filter(TransactionModel.transaction_date >= start_datetime)

    if endDate:
        end_datetime = datetime.fromisoformat(endDate.replace("Z", "+00:00"))
        query = query.filter(TransactionModel.transaction_date <= end_datetime)

    # Get total count before pagination
    total_count = query.count()

    # Apply sorting and pagination
    transactions = (
        query.order_by(TransactionModel.transaction_date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # Enrich transaction data with account information and calculate totals
    result_transactions = []
    for tx in transactions:
        tx_data = {
            "id": tx.id,
            "user_id": tx.user_id,
            "description": tx.description,
            "transaction_date": tx.transaction_date,
            "reference": tx.reference,
            "entries": [],
            "detailed_entries": [],
            "amount": 0.0,
        }

        # Process all entries
        for entry in tx.entries:
            account = db.query(Account).get(entry.account_id)
            if not account:
                continue

            entry_data = {
                "account_name": account.name,
                "account_type": account.account_type,
                "amount": float(entry.amount),
                "entry_type": entry.entry_type,
                "description": entry.description,
            }

            # Add to detailed entries list
            tx_data["detailed_entries"].append(entry_data)

            # For main view, only show user accounts and use them for total amount
            if account.account_type == "user":
                tx_data["entries"].append(entry_data)
                # For total amount, use the first user account entry
                if tx_data["amount"] == 0.0:
                    tx_data["amount"] = float(entry.amount)

        result_transactions.append(Transaction(**tx_data))

    # Calculate pagination info
    total_pages = (total_count + page_size - 1) // page_size

    return PaginatedTransactionResponse(
        transactions=result_transactions,
        total_count=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


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
