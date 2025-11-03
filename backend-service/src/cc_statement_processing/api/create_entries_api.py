from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.common.logger import get_logger
from src.database import get_db_session

from ..repositories.statement_repository import StatementRepository
from ..services.uob_statement_entry_service import UOBStatementEntryService
from .create_entries_schemas import (
    CreateEntriesRequest,
    CreateEntriesResponse,
    EntryPreview,
    PrepareEntriesResponse,
    TransactionPreview,
)
from .create_entries_utilities import (
    _build_transaction_previews,
    _get_account_by_id,
    _validate_accounts,
)

router = APIRouter()
log = get_logger(__name__)


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
        request: Request body with user_id, account IDs and mappings
        db: Database session

    Returns:
        Preview of transactions and entries that will be created

    Raises:
        HTTPException: If statement or accounts are not found, or don't belong to user
    """
    log.info(
        f"Preparing entries for statement {statement_id} by user {request.user_id}"
    )

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

    # Validate statement belongs to user
    if statement.user_id != request.user_id:
        raise HTTPException(
            status_code=403,
            detail=f"Statement {statement_id} does not belong to user {request.user_id}",
        )

    # Check if CSV output exists
    if not statement.csv_output:
        raise HTTPException(
            status_code=400,
            detail=f"Statement {statement_id} has not been processed yet",
        )

    # Validate all accounts exist and belong to user
    _validate_accounts(request, db)

    # Create a nested transaction to rollback changes
    # We'll use a savepoint to test the entries without committing
    try:
        # Create the service
        service = UOBStatementEntryService(
            db=db,
            user_id=request.user_id,
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
        request: Request body with user_id, account IDs and mappings
        db: Database session

    Returns:
        Summary of created transactions

    Raises:
        HTTPException: If statement or accounts are not found, or don't belong to user
    """
    log.info(f"Creating entries for statement {statement_id} by user {request.user_id}")

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

    # Validate statement belongs to user
    if statement.user_id != request.user_id:
        raise HTTPException(
            status_code=403,
            detail=f"Statement {statement_id} does not belong to user {request.user_id}",
        )

    # Check if CSV output exists
    if not statement.csv_output:
        raise HTTPException(
            status_code=400,
            detail=f"Statement {statement_id} has not been processed yet",
        )

    # Validate all accounts exist and belong to user
    _validate_accounts(request, db)

    try:
        # Create the service
        service = UOBStatementEntryService(
            db=db,
            user_id=request.user_id,
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
