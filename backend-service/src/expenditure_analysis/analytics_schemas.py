"""
Pydantic schemas for analytics endpoints.
"""

from __future__ import annotations

from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field, field_serializer


class AppBaseModel(BaseModel):
    class Config:
        from_attributes = True
        validate_by_name = True


# ============= Spending by Category Response Models =============


class CategorySpending(AppBaseModel):
    """Spending for a single category."""

    category: str
    amount: Decimal
    percentage: float = Field(description="Percentage of total spending")
    transaction_count: int
    average_transaction: Decimal

    @field_serializer("amount", "average_transaction")
    def serialize_decimals(self, value: Decimal) -> float:
        """Convert Decimal to float for JSON serialization."""
        return float(value)


class SpendingByCategoryResponse(AppBaseModel):
    """Response for spending by category endpoint."""

    categories: List[CategorySpending]
    total_spending: Decimal
    currency: str = "USD"

    @field_serializer("total_spending")
    def serialize_total_spending(self, value: Decimal) -> float:
        """Convert Decimal to float for JSON serialization."""
        return float(value)


# ============= Monthly Spending Response Models =============


class MonthlySpendingEntry(AppBaseModel):
    """Spending data for a single month."""

    month: str = Field(description="Month in YYYY-MM format")
    amount: Decimal
    transaction_count: int
    average_transaction: Decimal

    @field_serializer("amount", "average_transaction")
    def serialize_decimals(self, value: Decimal) -> float:
        """Convert Decimal to float for JSON serialization."""
        return float(value)


class MonthlySpendingResponse(AppBaseModel):
    """Response for monthly spending endpoint."""

    months: List[MonthlySpendingEntry]
    currency: str = "USD"
    total_spending: Decimal

    @field_serializer("total_spending")
    def serialize_total_spending(self, value: Decimal) -> float:
        """Convert Decimal to float for JSON serialization."""
        return float(value)


# ============= Insights Response Models =============


class CategorySummary(AppBaseModel):
    """Summary of spending in a category."""

    category: str
    amount: Decimal
    percentage: float

    @field_serializer("amount")
    def serialize_amount(self, value: Decimal) -> float:
        """Convert Decimal to float for JSON serialization."""
        return float(value)


class SummaryMetrics(AppBaseModel):
    """High-level summary metrics."""

    total_spending: Decimal
    average_spending_per_transaction: Decimal
    highest_spending_category: CategorySummary
    transaction_count: int

    @field_serializer("total_spending", "average_spending_per_transaction")
    def serialize_decimals(self, value: Decimal) -> float:
        """Convert Decimal to float for JSON serialization."""
        return float(value)


class MonthlyTrend(AppBaseModel):
    """Monthly spending for trend visualization."""

    month: str = Field(description="Month in YYYY-MM format")
    amount: Decimal

    @field_serializer("amount")
    def serialize_amount(self, value: Decimal) -> float:
        """Convert Decimal to float for JSON serialization."""
        return float(value)


class InsightsResponse(AppBaseModel):
    """Response for insights endpoint combining summary and trends."""

    summary: SummaryMetrics
    top_categories: List[CategorySummary]
    monthly_trend: List[MonthlyTrend]
    currency: str = "USD"
