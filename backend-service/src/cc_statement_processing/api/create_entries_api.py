from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from src.common.logger import get_logger
from src.database import get_db_session
from src.ledger.models.account import Account
from src.ledger.models.transaction import Transaction

from ..repositories.statement_repository import StatementRepository
from ..services.uob_statement_entry_service import UOBStatementEntryService

router = APIRouter()
log = get_logger(__name__)


class CategoryAccountMapping(BaseModel):
    """Mapping of category name to account ID"""

    category: str
    account_id: int


class CreateEntriesRequest(BaseModel):
    """Request model for creating ledger entries from a statement"""

    statement_id: int = Field(..., description="ID of the statement to process")
    credit_card_account_id: int = Field(
        ..., description="Account ID for the credit card liability account"
    )
    default_expense_account_id: int = Field(
        ...,
        description="Default account ID for expenses when category is not specified",
    )
    bank_account_id: Optional[int] = Field(
        None, description="Optional account ID for bank account (for payments/refunds)"
    )
    category_mappings: List[CategoryAccountMapping] = Field(
        default_factory=list,
        description="Optional mappings of category names to specific expense account IDs",
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


def _get_account_by_id(account_id: int, db: Session) -> Account:
    """
    Get an account by ID or raise HTTPException if not found.

    Args:
        account_id: ID of the account
        db: Database session

    Returns:
        Account object

    Raises:
        HTTPException: If account is not found
    """
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
    return account


def _validate_accounts(request: CreateEntriesRequest, db: Session) -> None:
    """
    Validate that all account IDs in the request exist.

    Args:
        request: The create entries request
        db: Database session

    Raises:
        HTTPException: If any account is not found
    """
    # Validate required accounts
    _get_account_by_id(request.credit_card_account_id, db)
    _get_account_by_id(request.default_expense_account_id, db)

    # Validate optional bank account
    if request.bank_account_id is not None:
        _get_account_by_id(request.bank_account_id, db)

    # Validate category mapping accounts
    for mapping in request.category_mappings:
        _get_account_by_id(mapping.account_id, db)


def _build_transaction_previews(
    transactions: List[Transaction], db: Session
) -> List[TransactionPreview]:
    """
    Build transaction preview objects from Transaction models.

    Args:
        transactions: List of Transaction objects
        db: Database session

    Returns:
        List of TransactionPreview objects
    """
    previews = []

    for txn in transactions:
        entry_previews = []
        for entry in txn.entries:
            account = _get_account_by_id(entry.account_id, db)
            entry_previews.append(
                EntryPreview(
                    account_id=entry.account_id,
                    account_name=account.name,
                    entry_type=entry.entry_type,
                    amount=float(entry.amount),
                    description=entry.description,
                )
            )

        previews.append(
            TransactionPreview(
                description=txn.description,
                transaction_date=txn.transaction_date.isoformat(),
                entries=entry_previews,
            )
        )

    return previews


@router.post(
    "/statements/{statement_id}/prepare-entries", response_model=PrepareEntriesResponse
)
def prepare_entries_from_statement(
    statement_id: int,
    request: CreateEntriesRequest,
    db: Session = Depends(get_db_session),
):
    """
    Prepare ledger entries from a statement without persisting them.
    This endpoint allows you to preview what entries will be created.

    Args:
        statement_id: ID of the statement to process
        request: Request body with account IDs and mappings
        db: Database session

    Returns:
        Preview of transactions and entries that will be created

    Raises:
        HTTPException: If statement or accounts are not found
    """
    log.info(f"Preparing entries for statement {statement_id}")

    # Validate statement ID in request matches path parameter
    if request.statement_id != statement_id:
        raise HTTPException(
            status_code=400,
            detail="Statement ID in path does not match request body",
        )

    # Get the statement
    statement = StatementRepository.get_statement_by_id(statement_id, db)
    if not statement:
        raise HTTPException(
            status_code=404, detail=f"Statement {statement_id} not found"
        )

    # Check if CSV output exists
    if not statement.csv_output:
        raise HTTPException(
            status_code=400,
            detail=f"Statement {statement_id} has not been processed yet",
        )

    # Validate all accounts exist
    _validate_accounts(request, db)

    # Create a nested transaction to rollback changes
    # We'll use a savepoint to test the entries without committing
    try:
        # Create the service
        service = UOBStatementEntryService(
            db=db,
            credit_card_account_id=request.credit_card_account_id,
            default_expense_account_id=request.default_expense_account_id,
            bank_account_id=request.bank_account_id,
        )

        # Set category mappings if provided
        if request.category_mappings:
            category_mapping = {
                mapping.category: mapping.account_id
                for mapping in request.category_mappings
            }
            service.set_category_account_mapping(category_mapping)

        # Create a savepoint
        db.begin_nested()

        # Process the CSV and create entries (will be rolled back)
        transactions = service.create_ledger_entries(statement.csv_output)

        # Build preview
        transaction_previews = _build_transaction_previews(transactions, db)

        # Calculate totals
        total_debits = sum(
            entry.amount
            for txn in transaction_previews
            for entry in txn.entries
            if entry.entry_type == "debit"
        )
        total_credits = sum(
            entry.amount
            for txn in transaction_previews
            for entry in txn.entries
            if entry.entry_type == "credit"
        )

        # Validate transactions
        is_balanced = service.validate_transactions(transactions)

        response = PrepareEntriesResponse(
            statement_id=statement_id,
            statement_filename=statement.filename,
            transactions=transaction_previews,
            total_transactions=len(transactions),
            total_debits=total_debits,
            total_credits=total_credits,
            is_balanced=is_balanced,
        )

        # Rollback the nested transaction
        db.rollback()

        log.info(
            f"Prepared {len(transactions)} transactions for statement {statement_id}"
        )
        return response

    except Exception as e:
        db.rollback()
        log.error(f"Error preparing entries for statement {statement_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error preparing entries: {str(e)}",
        )


@router.post(
    "/statements/{statement_id}/create-entries", response_model=CreateEntriesResponse
)
def create_entries_from_statement(
    statement_id: int,
    request: CreateEntriesRequest,
    db: Session = Depends(get_db_session),
):
    """
    Create ledger entries from a statement and persist them to the database.

    Args:
        statement_id: ID of the statement to process
        request: Request body with account IDs and mappings
        db: Database session

    Returns:
        Summary of created transactions

    Raises:
        HTTPException: If statement or accounts are not found
    """
    log.info(f"Creating entries for statement {statement_id}")

    # Validate statement ID in request matches path parameter
    if request.statement_id != statement_id:
        raise HTTPException(
            status_code=400,
            detail="Statement ID in path does not match request body",
        )

    # Get the statement
    statement = StatementRepository.get_statement_by_id(statement_id, db)
    if not statement:
        raise HTTPException(
            status_code=404, detail=f"Statement {statement_id} not found"
        )

    # Check if CSV output exists
    if not statement.csv_output:
        raise HTTPException(
            status_code=400,
            detail=f"Statement {statement_id} has not been processed yet",
        )

    # Validate all accounts exist
    _validate_accounts(request, db)

    try:
        # Create the service
        service = UOBStatementEntryService(
            db=db,
            credit_card_account_id=request.credit_card_account_id,
            default_expense_account_id=request.default_expense_account_id,
            bank_account_id=request.bank_account_id,
        )

        # Set category mappings if provided
        if request.category_mappings:
            category_mapping = {
                mapping.category: mapping.account_id
                for mapping in request.category_mappings
            }
            service.set_category_account_mapping(category_mapping)

        # Process the CSV and create entries (will be committed by the service)
        transactions = service.create_ledger_entries(statement.csv_output)

        # Validate transactions
        if not service.validate_transactions(transactions):
            raise HTTPException(
                status_code=400,
                detail="Created transactions are not balanced",
            )

        log.info(
            f"Successfully created {len(transactions)} transactions for statement {statement_id}"
        )

        return CreateEntriesResponse(
            statement_id=statement_id,
            transactions_created=len(transactions),
            message=f"Successfully created {len(transactions)} transactions from statement",
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        db.rollback()
        log.error(f"Error creating entries for statement {statement_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating entries: {str(e)}",
        )
