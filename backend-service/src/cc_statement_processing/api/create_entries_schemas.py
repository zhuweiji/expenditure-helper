from typing import List, Optional

from pydantic import BaseModel, Field


class CategoryAccountMapping(BaseModel):
    """Mapping of category name to account ID"""

    category: str
    account_id: int


class CreateEntriesRequest(BaseModel):
    """Request model for creating ledger entries from a statement"""

    statement_id: int = Field(..., description="ID of the statement to process")
    user_id: int = Field(..., description="ID of the user performing the operation")
    credit_card_account_id: Optional[int] = Field(
        None, description="Account ID for the credit card liability account"
    )
    default_expense_account_id: Optional[int] = Field(
        None,
        description="Default account ID for expenses when category is not specified",
    )
    bank_account_id: Optional[int] = Field(
        None, description="Optional account ID for bank account (for payments/refunds)"
    )
    category_mappings: List[CategoryAccountMapping] = Field(
        default_factory=list,
        description="Optional mappings of category names to specific expense account IDs",
    )

    dry_run: Optional[bool] = Field(
        True,
        description="If true, prepare entries without persisting them to the database",
    )


class EntryPreview(BaseModel):
    """Preview of a ledger entry to be created"""

    account_id: int
    account_name: str
    entry_type: str  # 'debit' or 'credit'
    amount: float
    description: str


class TransactionPreview(BaseModel):
    """Preview of a transaction to be created"""

    description: str
    transaction_date: str
    entries: List[EntryPreview]


class PrepareEntriesResponse(BaseModel):
    """Response model for prepared entries"""

    statement_id: int
    statement_filename: str
    transactions: List[TransactionPreview]
    total_transactions: int
    total_debits: float
    total_credits: float
    is_balanced: bool


class CreateEntriesResponse(BaseModel):
    """Response model for created entries"""

    statement_id: int
    transactions_created: int
    message: str
