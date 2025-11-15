from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from .entries_schemas import Entry, EntryCreate


class TransactionBase(BaseModel):
    description: str
    transaction_date: datetime
    reference: Optional[str] = None


class TransactionCreate(TransactionBase):
    user_id: int
    entries: List[EntryCreate] = []


class TransactionUpdate(TransactionBase):
    entries: Optional[List[EntryCreate]] = None


class TransactionEntry(BaseModel):
    account_name: str
    account_type: str
    amount: float
    entry_type: str  # 'debit' or 'credit'
    description: Optional[str] = None

    class Config:
        from_attributes = True


class Transaction(TransactionBase):
    id: int
    user_id: int
    amount: float = 0  # Total amount from entries
    entries: List[TransactionEntry] = []
    detailed_entries: List[TransactionEntry] = []  # For the detail view

    class Config:
        from_attributes = True


class PaginatedTransactionResponse(BaseModel):
    transactions: List[Transaction]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    page_size: int
    total_pages: int
