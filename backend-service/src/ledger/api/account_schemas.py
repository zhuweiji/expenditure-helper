from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, RootModel


class AppBaseModel(BaseModel):
    class Config:
        from_attributes = True
        validate_by_name = True


class MonthEntry(AppBaseModel):
    id: int
    entry_type: str
    amount: Decimal
    description: Optional[str] = None
    timestamp: datetime


class MonthTransaction(AppBaseModel):
    id: int
    date: datetime
    description: Optional[str] = None
    reference: Optional[str] = None
    entries: List[MonthEntry]


class AccountMonth(AppBaseModel):
    account_id: int
    account_name: str
    account_type: str
    total_debits: Decimal
    total_credits: Decimal
    transactions: List[MonthTransaction]


class MonthGroup(AppBaseModel):
    date: datetime
    month: str
    accounts: List[AccountMonth]


# --- Models for the single account transactions endpoint ---
class AccountEntry(AppBaseModel):
    id: int
    account_id: int
    # The service currently returns a key named "debit/debit" for the entry type.
    # Use alias so Pydantic can read that key into the `entry_type` field.
    entry_type: str = Field(..., alias="debit/debit")
    amount: Decimal
    description: Optional[str] = None
    transaction_id: Optional[int] = None
    timestamp: Optional[datetime] = None


class AccountTransaction(AppBaseModel):
    id: int
    date: datetime
    description: Optional[str] = None
    user_id: Optional[int] = None
    entries: List[AccountEntry]


class AccountTransactionsResponse(AppBaseModel):
    account_id: int
    account_name: str
    transactions: List[AccountTransaction]


class TransactionsByMonthResponse(RootModel[List[MonthGroup]]):
    pass
