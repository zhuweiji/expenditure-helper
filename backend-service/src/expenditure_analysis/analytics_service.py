"""
Service layer for analytics operations.
Handles business logic for spending analysis and insights.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session
from src.ledger.models import Account, Entry, Transaction


def get_spending_by_category(
    user_id: int,
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    currency: str = "USD",
) -> dict:
    """
    Get spending aggregated by expense category (account name) for a given date range.

    Args:
        user_id: The user's ID
        db: Database session
        start_date: Optional start date (ISO format date string will be converted by caller)
        end_date: Optional end date (ISO format date string will be converted by caller)
        currency: Currency code (for response only, no conversion performed)

    Returns:
        Dictionary with categories list, total spending, and currency
    """
    # Get all expense accounts for the user (only expense accounts are spending categories)
    expense_accounts = (
        db.query(Account)
        .filter(Account.user_id == user_id, Account.account_type == "expense")
        .all()
    )

    if not expense_accounts:
        return {
            "categories": [],
            "total_spending": Decimal("0.00"),
            "currency": currency,
        }

    expense_account_ids = [acc.id for acc in expense_accounts]

    # Build query for entries in expense accounts
    query = db.query(Entry).filter(Entry.account_id.in_(expense_account_ids))

    # Filter by date range if provided
    if start_date:
        query = query.filter(Entry.timestamp >= start_date)
    if end_date:
        query = query.filter(Entry.timestamp <= end_date)

    entries = query.all()

    # Group spending by category (account name)
    category_data: dict = defaultdict(
        lambda: {"amount": Decimal("0.00"), "transaction_count": 0, "entries": []}
    )

    for entry in entries:
        account = next((acc for acc in expense_accounts if acc.id == entry.account_id))
        category_name = account.name

        # Only count debits (spending) for expense accounts
        if entry.entry_type == "debit":
            category_data[category_name]["amount"] += entry.amount
            category_data[category_name]["entries"].append(entry)

    # Remove categories with zero spending
    category_data = {k: v for k, v in category_data.items() if v["amount"] > 0}

    # Calculate metrics for each category
    total_spending = Decimal("0.00")
    categories = []

    for category_name, data in sorted(
        category_data.items(), key=lambda x: x[1]["amount"], reverse=True
    ):
        amount = data["amount"]
        total_spending += amount

        categories.append(
            {
                "category": category_name,
                "amount": amount,
                "percentage": 0.0,  # Will be calculated below
                "transaction_count": len(data["entries"]),
                "average_transaction": Decimal("0.00"),  # Will be calculated below
            }
        )

    # Calculate percentages and averages
    if total_spending > 0:
        for cat in categories:
            cat["percentage"] = round(float((cat["amount"] / total_spending) * 100), 1)
            if cat["transaction_count"] > 0:
                cat["average_transaction"] = cat["amount"] / cat["transaction_count"]

    return {
        "categories": categories,
        "total_spending": total_spending,
        "currency": currency,
    }


def get_monthly_spending(
    user_id: int,
    db: Session,
    months: int = 12,
    currency: str = "USD",
) -> dict:
    """
    Get spending aggregated by month for trend analysis.

    Args:
        user_id: The user's ID
        db: Database session
        months: Number of months to return (default: 12)
        currency: Currency code (for response only)

    Returns:
        Dictionary with months list, total spending, and currency
    """
    # Get all expense accounts for the user
    expense_accounts = (
        db.query(Account)
        .filter(Account.user_id == user_id, Account.account_type == "expense")
        .all()
    )

    if not expense_accounts:
        return {
            "months": [],
            "currency": currency,
            "total_spending": Decimal("0.00"),
        }

    expense_account_ids = [acc.id for acc in expense_accounts]

    # Calculate the date range for the last N months
    now = datetime.utcnow()
    start_date = now - timedelta(days=30 * months)

    # Get entries in the date range
    entries = (
        db.query(Entry)
        .join(Transaction)
        .filter(
            and_(
                Entry.account_id.in_(expense_account_ids),
                Entry.entry_type == "debit",
                Entry.timestamp >= start_date,
            )
        )
        .all()
    )

    # Group by month
    monthly_data: dict = defaultdict(lambda: {"amount": Decimal("0.00"), "entries": []})

    for entry in entries:
        # Get month key in YYYY-MM format
        month_key = entry.timestamp.strftime("%Y-%m")
        monthly_data[month_key]["amount"] += entry.amount  # type: ignore
        monthly_data[month_key]["entries"].append(entry)  # type: ignore

    # Sort by month (oldest first)
    months_list = []
    total_spending = Decimal("0.00")

    for month_key in sorted(monthly_data.keys()):
        data = monthly_data[month_key]
        amount = data["amount"]
        transaction_count = len(data["entries"])
        average_transaction = (
            amount / transaction_count if transaction_count > 0 else Decimal("0.00")
        )

        months_list.append(
            {
                "month": month_key,
                "amount": amount,
                "transaction_count": transaction_count,
                "average_transaction": average_transaction,
            }
        )
        total_spending += amount

    return {
        "months": months_list,
        "currency": currency,
        "total_spending": total_spending,
    }


def get_insights(
    user_id: int,
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> dict:
    """
    Get a summary view with key metrics combining spending by category and monthly trends.

    Args:
        user_id: The user's ID
        db: Database session
        start_date: Optional start date for the analysis
        end_date: Optional end date for the analysis

    Returns:
        Dictionary with summary metrics, top categories, and monthly trends
    """
    currency = "USD"

    # Get spending by category
    category_data = get_spending_by_category(
        user_id, db, start_date, end_date, currency
    )

    # Get monthly spending (full history for trends)
    monthly_data = get_monthly_spending(user_id, db, months=12, currency=currency)

    # Calculate summary metrics
    categories = category_data["categories"]
    total_spending = category_data["total_spending"]

    # Count total transactions across all categories
    total_transactions = sum(cat["transaction_count"] for cat in categories)

    # Calculate average spending per transaction
    average_per_transaction = (
        total_spending / total_transactions
        if total_transactions > 0
        else Decimal("0.00")
    )

    # Get highest spending category
    highest_category = categories[0] if categories else None
    highest_spending_category = (
        {
            "category": highest_category["category"],
            "amount": highest_category["amount"],
            "percentage": highest_category["percentage"],
        }
        if highest_category
        else {
            "category": "N/A",
            "amount": Decimal("0.00"),
            "percentage": 0.0,
        }
    )

    # Get top 3 categories (or all if fewer)
    top_categories = [
        {
            "category": cat["category"],
            "amount": cat["amount"],
            "percentage": cat["percentage"],
        }
        for cat in categories[:3]
    ]

    # Get monthly trend (convert to simplified format)
    monthly_trend = [
        {"month": month["month"], "amount": month["amount"]}
        for month in monthly_data["months"]
    ]

    return {
        "summary": {
            "total_spending": total_spending,
            "average_spending_per_transaction": average_per_transaction,
            "highest_spending_category": highest_spending_category,
            "transaction_count": total_transactions,
        },
        "top_categories": top_categories,
        "monthly_trend": monthly_trend,
        "currency": currency,
    }
