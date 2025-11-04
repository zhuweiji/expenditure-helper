"""
User service for creating default accounts and other user-related operations.
"""

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.orm import Session

from ..models.account import Account


def create_default_accounts_for_user(db: Session, user_id: int) -> list[Account]:
    """
    Create a minimal chart of accounts for a new user to support credit card statement processing.

    This creates accounts in the following categories:
    - Assets: Bank account for payments/refunds
    - Liabilities: Credit card account
    - Equity: Opening balance equity for initial setup
    - Expenses: General and categorized expense accounts

    Args:
        db: Database session
        user_id: The user's ID

    Returns:
        List of created Account objects
    """

    default_accounts = [
        # ASSETS - For payment transactions
        {"name": "Bank Account", "account_type": "asset", "balance": Decimal("0.00")},
        # LIABILITIES - Credit card tracking
        {
            "name": "Credit Card",
            "account_type": "liability",
            "balance": Decimal("0.00"),
        },
        # EQUITY - For opening balances
        {
            "name": "Opening Balance Equity",
            "account_type": "equity",
            "balance": Decimal("0.00"),
        },
        # EXPENSES - Spending categories
        {
            "name": "General Expenses",
            "account_type": "expense",
            "balance": Decimal("0.00"),
        },
        {
            "name": "Food & Dining",
            "account_type": "expense",
            "balance": Decimal("0.00"),
        },
        {"name": "Groceries", "account_type": "expense", "balance": Decimal("0.00")},
        {
            "name": "Transportation",
            "account_type": "expense",
            "balance": Decimal("0.00"),
        },
        {
            "name": "Entertainment",
            "account_type": "expense",
            "balance": Decimal("0.00"),
        },
        {"name": "Shopping", "account_type": "expense", "balance": Decimal("0.00")},
    ]

    created_accounts = []
    for account_data in default_accounts:
        account = Account(
            user_id=user_id,
            name=account_data["name"],
            account_type=account_data["account_type"],
            balance=account_data["balance"],
        )
        db.add(account)
        created_accounts.append(account)

    # No commit here - let the caller handle transaction management
    return created_accounts


def get_user_account_summary(db: Session, user_id: int) -> dict:
    """
    Get a summary of all accounts for a user, grouped by type.

    Args:
        db: Database session
        user_id: The user's ID

    Returns:
        Dictionary with account types as keys and lists of accounts as values
    """
    accounts = db.query(Account).filter(Account.user_id == user_id).all()

    summary = {
        "asset": [],
        "liability": [],
        "equity": [],
        "revenue": [],
        "expense": [],
        "unspecified": [],
    }

    for account in accounts:
        account_type = account.account_type or "unspecified"
        if account_type not in summary:
            summary[account_type] = []
        summary[account_type].append(
            {"id": account.id, "name": account.name, "balance": float(account.balance)}
        )

    return summary


def calculate_net_worth(db: Session, user_id: int) -> Decimal:
    """
    Calculate a user's net worth (Assets - Liabilities).

    Args:
        db: Database session
        user_id: The user's ID

    Returns:
        Net worth as a Decimal
    """
    accounts = db.query(Account).filter(Account.user_id == user_id).all()

    assets = sum(
        account.balance for account in accounts if account.account_type == "asset"
    )
    liabilities = sum(
        account.balance for account in accounts if account.account_type == "liability"
    )

    return Decimal(str(assets)) - Decimal(str(liabilities))


@dataclass
class DefaultAccounts:
    credit_card_account_id: int | None
    bank_account_id: int | None
    default_expense_account_id: int | None


def get_default_accounts(user_id: int, db: Session) -> DefaultAccounts:
    """
    Find default accounts by conventional names.
    """
    accounts = db.query(Account).filter(Account.user_id == user_id).all()

    # Find by name conventions
    credit_card = next((a for a in accounts if a.name == "Credit Card"), None)
    bank = next((a for a in accounts if a.name == "Bank Account"), None)
    expense = next((a for a in accounts if a.name == "General Expenses"), None)

    return DefaultAccounts(
        credit_card_account_id=credit_card.id if credit_card else None,
        bank_account_id=bank.id if bank else None,
        default_expense_account_id=expense.id if expense else None,
    )
