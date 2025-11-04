"""
User service for creating default accounts and other user-related operations.
"""

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from ..models import Account, Entry, Transaction


def get_transactions_grouped_by_month(user_id: int, db: Session) -> list[dict]:
    """
    Get all transactions for a user, grouped by month.

    Args:
        user_id: The user's ID
        db: Database session

    Returns:
        List of dictionaries with month information and account transactions:
        [
            {
                'date': datetime(2025, 1, 1),  # First day of the month
                'month': 'January 2025',
                'accounts': [
                    {
                        'account_id': 1,
                        'account_name': 'Credit Card',
                        'account_type': 'liability',
                        'total_debits': Decimal('100.00'),
                        'total_credits': Decimal('50.00'),
                        'transactions': [
                            {
                                'id': 1,
                                'date': datetime,
                                'description': 'Purchase at Store',
                                'entries': [...]
                            },
                            ...
                        ]

                    },
                    ...
                ]
            },
            ...
        ]
    """
    # Get all accounts for the user
    accounts = db.query(Account).filter(Account.user_id == user_id).all()

    # Get all transactions for the user
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .order_by(Transaction.transaction_date.desc())
        .all()
    )

    # Group transactions by month
    months_dict = defaultdict(lambda: defaultdict(list))

    for transaction in transactions:
        # Get the month key (first day of the month)
        month_date = transaction.transaction_date.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        month_key = month_date.strftime("%Y-%m")

        # Get all entries for this transaction
        entries = db.query(Entry).filter(Entry.transaction_id == transaction.id).all()

        # Group entries by account
        for entry in entries:
            account = next((a for a in accounts if a.id == entry.account_id), None)
            if account:
                transaction_data = {
                    "id": transaction.id,
                    "date": transaction.transaction_date,
                    "description": transaction.description,
                    "reference": transaction.reference,
                    "entries": [],
                }

                # Find if we already have this transaction for this account in this month
                account_transactions = months_dict[month_key][entry.account_id]
                existing_transaction = next(
                    (t for t in account_transactions if t["id"] == transaction.id), None
                )

                if existing_transaction:
                    # Add entry to existing transaction
                    existing_transaction["entries"].append(
                        {
                            "id": entry.id,
                            "entry_type": entry.entry_type,
                            "amount": entry.amount,
                            "description": entry.description,
                            "timestamp": entry.timestamp,
                        }
                    )
                else:
                    # Create new transaction with this entry
                    transaction_data["entries"].append(
                        {
                            "id": entry.id,
                            "entry_type": entry.entry_type,
                            "amount": entry.amount,
                            "description": entry.description,
                            "timestamp": entry.timestamp,
                        }
                    )
                    months_dict[month_key][entry.account_id].append(transaction_data)

    # Convert to final format
    result = []
    for month_key in sorted(months_dict.keys(), reverse=True):
        month_date = datetime.strptime(month_key, "%Y-%m")
        month_name = month_date.strftime("%B %Y")

        accounts_data = []
        for account_id, transactions_list in months_dict[month_key].items():
            account = next((a for a in accounts if a.id == account_id), None)
            if account:
                # Calculate totals
                total_debits = Decimal("0.00")
                total_credits = Decimal("0.00")

                for trans in transactions_list:
                    for entry in trans["entries"]:
                        if entry["entry_type"] == "debit":
                            total_debits += entry["amount"]
                        elif entry["entry_type"] == "credit":
                            total_credits += entry["amount"]

                accounts_data.append(
                    {
                        "account_id": account.id,
                        "account_name": account.name,
                        "account_type": account.account_type,
                        "total_debits": total_debits,
                        "total_credits": total_credits,
                        "transactions": transactions_list,
                    }
                )

        result.append(
            {"date": month_date, "month": month_name, "accounts": accounts_data}
        )

    return result


def get_transactions_for_account(account_id: int, user_id: int, db: Session):
    # Verify account exists and belongs to user
    account = (
        db.query(Account)
        .filter(Account.id == account_id, Account.user_id == user_id)
        .first()
    )

    if account is None:
        return

    # Get all entries for this account with their transactions
    entries = (
        db.query(Entry)
        .join(Transaction)
        .filter(Entry.account_id == account_id)
        .order_by(Transaction.transaction_date.desc())
        .all()
    )

    # Group entries by transaction
    transactions_dict = {}
    for entry in entries:
        transaction = entry.transaction
        if transaction.id not in transactions_dict:
            transactions_dict[transaction.id] = {
                "id": transaction.id,
                "date": transaction.transaction_date,
                "description": transaction.description,
                "user_id": transaction.user_id,
                "entries": [],
            }
        transactions_dict[transaction.id]["entries"].append(
            {
                "id": entry.id,
                "account_id": entry.account_id,
                "debit/debit": entry.entry_type,
                "amount": entry.amount,
                "description": entry.description,
                "transaction_id": entry.transaction_id,
                "timestamp": entry.timestamp,
            }
        )

    return {
        "account_id": account_id,
        "account_name": account.name,
        "transactions": list(transactions_dict.values()),
    }


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
