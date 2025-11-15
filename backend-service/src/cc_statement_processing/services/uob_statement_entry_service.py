import csv
from datetime import datetime
from decimal import Decimal
from io import StringIO
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from src.common.logger import get_logger
from src.ledger.models.entry import Entry
from src.ledger.models.transaction import Transaction

log = get_logger(__name__)


class UOBStatementEntryService:
    """
    Service to process UOB credit card statement CSV data and create
    double-entry ledger transactions.
    """

    def __init__(
        self,
        db: Session,
        user_id: int,
        credit_card_account_id: int,
        default_expense_account_id: int,
        bank_account_id: Optional[int] = None,
    ):
        """
        Initialize the service.

        Args:
            db: Database session
            user_id: ID of the user who owns the transactions
            credit_card_account_id: Account ID for the credit card liability account
            default_expense_account_id: Default account ID for expenses when category is not specified
            bank_account_id: Optional account ID for bank account (used for payments/refunds)
        """
        self.db = db
        self.user_id = user_id
        self.credit_card_account_id = credit_card_account_id
        self.default_expense_account_id = default_expense_account_id
        self.bank_account_id = bank_account_id
        self.category_account_mapping: Dict[str, int] = {}

    def set_category_account_mapping(self, mapping: Dict[str, int]) -> None:
        """
        Set the mapping of category names to account IDs.

        Args:
            mapping: Dictionary mapping category names to account IDs
        """
        self.category_account_mapping = mapping

    def create_ledger_entries(self, csv_content: str) -> List[Transaction]:
        """
        Process CSV content and create ledger transactions and entries.

        Convenience method that combines build_ledger_entries_data and persist_ledger_entries.
        For more control, use build_ledger_entries_data and persist_ledger_entries separately.

        Args:
            csv_content: CSV string content

        Returns:
            List of created Transaction objects
        """
        transactions_data = UOBStatementEntryService.build_ledger_entries_data(
            csv_content,
            self.credit_card_account_id,
            self.default_expense_account_id,
            self.category_account_mapping,
            self.bank_account_id,
        )
        transactions = self.create_ledger_objects(
            user_id=self.user_id, transactions_data=transactions_data
        )
        return self.persist_ledger_objects(transactions)

    @staticmethod
    def build_ledger_entries_data(
        csv_content: str,
        credit_card_account_id: int,
        default_expense_account_id: int,
        category_account_mapping: Optional[Dict[str, int]] = None,
        bank_account_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Process CSV content and build ledger transaction data (pure function).

        This is a pure static function that does not modify the database or depend
        on instance state. It returns the data structure representing transactions
        and entries based on the provided configuration.

        For credit card purchases (positive amounts):
        - Debit: Expense account (increases expense)
        - Credit: Credit card liability account (increases liability)

        For payments/refunds (negative amounts):
        - Debit: Credit card liability account (decreases liability)
        - Credit: Bank account or default expense account (decreases asset/reverses expense)

        Args:
            csv_content: CSV string content
            credit_card_account_id: Account ID for the credit card liability account
            default_expense_account_id: Default account ID for expenses
            category_account_mapping: Optional mapping of category names to account IDs
            bank_account_id: Optional account ID for bank account (used for payments/refunds)

        Returns:
            List of dictionaries representing transaction data with entries
        """
        if category_account_mapping is None:
            category_account_mapping = {}

        parsed_transactions = UOBStatementEntryService.parse_csv(csv_content)
        transactions_data = []

        for txn_data in parsed_transactions:
            if txn_data["is_payment_or_refund"]:
                # Handle payment or refund
                transaction_data = (
                    UOBStatementEntryService._build_payment_transaction_data(
                        txn_data,
                        credit_card_account_id,
                        default_expense_account_id,
                        bank_account_id,
                    )
                )
            else:
                # Handle regular purchase
                transaction_data = (
                    UOBStatementEntryService._build_purchase_transaction_data(
                        txn_data,
                        credit_card_account_id,
                        default_expense_account_id,
                        category_account_mapping,
                    )
                )

            transactions_data.append(transaction_data)

        return transactions_data

    @classmethod
    def create_ledger_objects(
        cls, user_id: int, transactions_data: List[Dict[str, Any]]
    ) -> List[Transaction]:
        """
        Create ledger transaction objects from transaction data (in memory).

        Takes the output from build_ledger_entries_data and creates actual
        Transaction and Entry objects in memory.

        Args:
            transactions_data: List of transaction data dictionaries from build_ledger_entries_data

        Returns:
            List of created Transaction objects
        """
        created_transactions = []

        for txn_data in transactions_data:
            # Create the transaction
            transaction = Transaction(
                user_id=user_id,
                description=txn_data["description"],
                transaction_date=txn_data["date"],
                reference=None,
            )

            # Create entries
            for entry_data in txn_data["entries"]:
                entry = Entry(
                    transaction_id=transaction.id,
                    account_id=entry_data["account_id"],
                    entry_type=entry_data["entry_type"],
                    amount=entry_data["amount"],
                    description=entry_data["description"],
                    timestamp=entry_data["timestamp"],
                )
                transaction.entries.append(entry)

            created_transactions.append(transaction)

        return created_transactions

    def persist_ledger_objects(
        self, transactions: List[Transaction]
    ) -> list[Transaction]:
        """
        Persist a list of Transaction objects to the database.

        Args:
            transactions: List of Transaction objects to persist

        Returns:
            List of persisted Transaction objects
        """
        for transaction in transactions:
            self.db.add(transaction)
            for entry in transaction.entries:
                self.db.add(entry)

        self.db.commit()

        return transactions

    @staticmethod
    def _build_purchase_transaction_data(
        txn_data: Dict[str, Any],
        credit_card_account_id: int,
        default_expense_account_id: int,
        category_account_mapping: Dict[str, int],
    ) -> Dict[str, Any]:
        """
        Build data structure for a credit card purchase transaction (pure function).

        Args:
            txn_data: Parsed transaction data
            credit_card_account_id: Account ID for the credit card liability account
            default_expense_account_id: Default account ID for expenses
            category_account_mapping: Mapping of category names to account IDs

        Returns:
            Dictionary representing the transaction and its entries
        """
        # Determine the expense account based on category
        expense_account_id = default_expense_account_id
        if txn_data["category"] and txn_data["category"] in category_account_mapping:
            expense_account_id = category_account_mapping[txn_data["category"]]

        return {
            "description": txn_data["description"],
            "date": txn_data["date"],
            "entries": [
                {
                    "account_id": expense_account_id,
                    "entry_type": "debit",
                    "amount": txn_data["amount"],
                    "description": txn_data["description"],
                    "timestamp": txn_data["date"],
                },
                {
                    "account_id": credit_card_account_id,
                    "entry_type": "credit",
                    "amount": txn_data["amount"],
                    "description": txn_data["description"],
                    "timestamp": txn_data["date"],
                },
            ],
        }

    @staticmethod
    def _build_payment_transaction_data(
        txn_data: Dict[str, Any],
        credit_card_account_id: int,
        default_expense_account_id: int,
        bank_account_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Build data structure for a credit card payment or refund transaction (pure function).

        Args:
            txn_data: Parsed transaction data
            credit_card_account_id: Account ID for the credit card liability account
            default_expense_account_id: Default account ID for expenses
            bank_account_id: Optional account ID for bank account

        Returns:
            Dictionary representing the transaction and its entries
        """
        # Use bank account if provided, otherwise use default expense account
        contra_account_id = (
            bank_account_id
            if bank_account_id is not None
            else default_expense_account_id
        )

        return {
            "description": txn_data["description"],
            "date": txn_data["date"],
            "entries": [
                {
                    "account_id": credit_card_account_id,
                    "entry_type": "debit",
                    "amount": txn_data["amount"],
                    "description": txn_data["description"],
                    "timestamp": txn_data["date"],
                },
                {
                    "account_id": contra_account_id,
                    "entry_type": "credit",
                    "amount": txn_data["amount"],
                    "description": txn_data["description"],
                    "timestamp": txn_data["date"],
                },
            ],
        }

    @classmethod
    def validate_transactions(cls, transactions: List[Transaction]) -> bool:
        """
        Validate that all transactions are balanced (total debits = total credits).

        Args:
            transactions: List of Transaction objects to validate

        Returns:
            True if all transactions are balanced, False otherwise
        """
        for transaction in transactions:
            total_debits = sum(
                entry.amount
                for entry in transaction.entries
                if entry.entry_type == "debit"
            )
            total_credits = sum(
                entry.amount
                for entry in transaction.entries
                if entry.entry_type == "credit"
            )

            if total_debits != total_credits:
                return False

        return True

    @classmethod
    def parse_csv(cls, csv_content: str) -> List[Dict[str, Any]]:
        """
        Parse CSV content from UOB credit card statement.

        Args:
            csv_content: CSV string content

        Returns:
            List of dictionaries containing parsed transaction data
        """
        csv_file = StringIO(csv_content)
        reader = csv.DictReader(csv_file)

        transactions = []
        for row in reader:
            # Parse the row, keeping the sign of the amount
            amount = Decimal(row["Amount"])

            # Parse the row
            transaction_data = {
                "date": datetime.strptime(row["Date"], "%Y-%m-%d"),
                "description": row.get("Description", ""),
                "amount": abs(amount),  # Store absolute value
                "is_payment_or_refund": amount < 0,  # Negative = payment/refund
                "category": row.get("Category", "") or None,
            }
            transactions.append(transaction_data)

        return transactions
