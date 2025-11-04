from dataclasses import dataclass
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.common.logger import get_logger
from src.ledger.models.account import Account
from src.ledger.models.transaction import Transaction
from src.ledger.services.user_service import get_default_accounts

from .create_entries_schemas import (
    CreateEntriesRequest,
    EntryPreview,
    TransactionPreview,
)

log = get_logger(__name__)


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


@dataclass
class RequiredCCStatementAccounts:
    credit_card_account: Account
    default_expense_account: Account
    bank_account: Optional[Account]


def resolve_user_accounts(
    request: CreateEntriesRequest, db: Session
) -> RequiredCCStatementAccounts:
    """
    If account ids are provided: validate that all account IDs in the request exist and belong to the user
    If there are missing account ids: then use default accounts for the user

    Args:
        request: The create entries request
        db: Database session

    Raises:
        HTTPException: If any account is not found or doesn't belong to the user
    """
    default_accounts = get_default_accounts(request.user_id, db)

    # Validate required accounts
    credit_card_account_id = (
        request.credit_card_account_id or default_accounts.credit_card_account_id
    )
    if credit_card_account_id is None:
        raise HTTPException(
            status_code=400,
            detail="Credit card account ID is required but not provided and no default found",
        )

    credit_card_account = _get_account_by_id(credit_card_account_id, db)
    if credit_card_account.user_id != request.user_id:
        raise HTTPException(
            status_code=403,
            detail=f"Account {request.credit_card_account_id} does not belong to user {request.user_id}",
        )

    default_expense_account_id = (
        request.default_expense_account_id
        or default_accounts.default_expense_account_id
    )

    if default_expense_account_id is None:
        raise HTTPException(
            status_code=400,
            detail="Default expense account ID is required but not provided and no default found",
        )

    default_expense_account = _get_account_by_id(default_expense_account_id, db)
    if default_expense_account.user_id != request.user_id:
        raise HTTPException(
            status_code=403,
            detail=f"Account {request.default_expense_account_id} does not belong to user {request.user_id}",
        )

    # Validate optional bank account
    bank_account = None
    if request.bank_account_id is not None:
        bank_account = _get_account_by_id(request.bank_account_id, db)
        if bank_account.user_id != request.user_id:
            raise HTTPException(
                status_code=403,
                detail=f"Account {request.bank_account_id} does not belong to user {request.user_id}",
            )

    # Validate category mapping accounts
    for mapping in request.category_mappings:
        account = _get_account_by_id(mapping.account_id, db)
        if account.user_id != request.user_id:
            raise HTTPException(
                status_code=403,
                detail=f"Account {mapping.account_id} does not belong to user {request.user_id}",
            )

    return RequiredCCStatementAccounts(
        credit_card_account=credit_card_account,
        default_expense_account=default_expense_account,
        bank_account=bank_account,
    )


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
