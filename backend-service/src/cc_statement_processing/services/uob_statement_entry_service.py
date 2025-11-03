import csv
from datetime import datetime
from decimal import Decimal
from io import StringIO
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from src.ledger.models.entry import Entry
from src.ledger.models.transaction import Transaction


class UOBStatementEntryService:
    """
    Service to process UOB credit card statement CSV data and create
    double-entry ledger transactions.
    """

    def __init__(
        self,
        db: Session,
        credit_card_account_id: int,
        default_expense_account_id: int,
        bank_account_id: Optional[int] = None,
    ):
        """
        Initialize the service.

        Args:
            db: Database session
            credit_card_account_id: Account ID for the credit card liability account
            default_expense_account_id: Default account ID for expenses when category is not specified
            bank_account_id: Optional account ID for bank account (used for payments/refunds)
        """
        self.db = db
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

    def parse_csv(self, csv_content: str) -> List[Dict[str, Any]]:
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
                "description": row["Description"].strip(),
                "amount": abs(amount),  # Store absolute value
                "is_payment_or_refund": amount < 0,  # Negative = payment/refund
                "category": row.get("Category", "").strip() or None,
            }
            transactions.append(transaction_data)

        return transactions

    def create_ledger_entries(self, csv_content: str) -> List[Transaction]:
        """
        Process CSV content and create ledger transactions and entries.

        For credit card purchases (positive amounts):
        - Debit: Expense account (increases expense)
        - Credit: Credit card liability account (increases liability)

        For payments/refunds (negative amounts):
        - Debit: Credit card liability account (decreases liability)
        - Credit: Bank account or default expense account (decreases asset/reverses expense)

        Args:
            csv_content: CSV string content

        Returns:
            List of created Transaction objects
        """
        parsed_transactions = self.parse_csv(csv_content)
        created_transactions = []

        for txn_data in parsed_transactions:
            if txn_data["is_payment_or_refund"]:
                # Handle payment or refund
                transaction = self._create_payment_transaction(txn_data)
            else:
                # Handle regular purchase
                transaction = self._create_purchase_transaction(txn_data)

            created_transactions.append(transaction)

        # Commit all changes
        self.db.commit()

        return created_transactions

    def _create_purchase_transaction(self, txn_data: Dict[str, Any]) -> Transaction:
        """
        Create a transaction for a credit card purchase.

        Args:
            txn_data: Parsed transaction data

        Returns:
            Created Transaction object
        """
        # Determine the expense account based on category
        expense_account_id = self.default_expense_account_id
        if (
            txn_data["category"]
            and txn_data["category"] in self.category_account_mapping
        ):
            expense_account_id = self.category_account_mapping[txn_data["category"]]

        # Create the transaction
        transaction = Transaction(
            description=txn_data["description"],
            transaction_date=txn_data["date"],
            reference=None,
        )
        self.db.add(transaction)
        self.db.flush()

        # Create debit entry (expense account)
        debit_entry = Entry(
            transaction_id=transaction.id,
            account_id=expense_account_id,
            entry_type="debit",
            amount=txn_data["amount"],
            description=txn_data["description"],
            timestamp=txn_data["date"],
        )
        self.db.add(debit_entry)

        # Create credit entry (credit card liability account)
        credit_entry = Entry(
            transaction_id=transaction.id,
            account_id=self.credit_card_account_id,
            entry_type="credit",
            amount=txn_data["amount"],
            description=txn_data["description"],
            timestamp=txn_data["date"],
        )
        self.db.add(credit_entry)

        return transaction

    def _create_payment_transaction(self, txn_data: Dict[str, Any]) -> Transaction:
        """
        Create a transaction for a credit card payment or refund.

        Args:
            txn_data: Parsed transaction data

        Returns:
            Created Transaction object
        """
        # Use bank account if provided, otherwise use default expense account
        contra_account_id = (
            self.bank_account_id
            if self.bank_account_id is not None
            else self.default_expense_account_id
        )

        # Create the transaction
        transaction = Transaction(
            description=txn_data["description"],
            transaction_date=txn_data["date"],
            reference=None,
        )
        self.db.add(transaction)
        self.db.flush()

        # Create debit entry (credit card liability account - decreases liability)
        debit_entry = Entry(
            transaction_id=transaction.id,
            account_id=self.credit_card_account_id,
            entry_type="debit",
            amount=txn_data["amount"],
            description=txn_data["description"],
            timestamp=txn_data["date"],
        )
        self.db.add(debit_entry)

        # Create credit entry (bank account or expense account - decreases asset/reverses expense)
        credit_entry = Entry(
            transaction_id=transaction.id,
            account_id=contra_account_id,
            entry_type="credit",
            amount=txn_data["amount"],
            description=txn_data["description"],
            timestamp=txn_data["date"],
        )
        self.db.add(credit_entry)

        return transaction

    def validate_transactions(self, transactions: List[Transaction]) -> bool:
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
