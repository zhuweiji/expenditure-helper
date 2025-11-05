from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.database import get_db_session

from .analytics_schemas import (
    InsightsResponse,
    MonthlySpendingResponse,
    SpendingByCategoryResponse,
)
from .analytics_service import (
    get_insights,
    get_monthly_spending,
    get_spending_by_category,
)

router = APIRouter()


def parse_iso_date(date_string: str) -> datetime:
    """Parse ISO format date string (YYYY-MM-DD) to datetime."""
    try:
        return datetime.fromisoformat(date_string)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date format. Please use ISO format (YYYY-MM-DD): {date_string}",
        )


@router.get(
    "/spending-by-category",
    response_model=SpendingByCategoryResponse,
    summary="Get spending aggregated by category",
)
def spending_by_category(
    user_id: int = Query(..., description="The user's ID"),
    start_date: Optional[str] = Query(
        None, description="Start date in ISO format (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = Query(
        None, description="End date in ISO format (YYYY-MM-DD)"
    ),
    currency: str = Query("USD", description="Currency code"),
    db: Session = Depends(get_db_session),
) -> SpendingByCategoryResponse:
    """
    Get spending aggregated by category/account for a given date range.

    Returns spending data grouped by expense category with percentages and transaction metrics.
    """
    # Parse dates if provided
    start_dt = parse_iso_date(start_date) if start_date else None
    end_dt = parse_iso_date(end_date) if end_date else None

    result = get_spending_by_category(
        user_id=user_id,
        db=db,
        start_date=start_dt,
        end_date=end_dt,
        currency=currency,
    )

    return SpendingByCategoryResponse(**result)


@router.get(
    "/monthly-spending",
    response_model=MonthlySpendingResponse,
    summary="Get spending aggregated by month",
)
def monthly_spending(
    user_id: int = Query(..., description="The user's ID"),
    months: int = Query(
        12, ge=1, le=60, description="Number of months to return (default: 12)"
    ),
    currency: str = Query("USD", description="Currency code"),
    db: Session = Depends(get_db_session),
) -> MonthlySpendingResponse:
    """
    Get spending aggregated by month for trend analysis.

    Returns monthly spending data useful for visualizing spending trends over time.
    """
    result = get_monthly_spending(
        user_id=user_id,
        db=db,
        months=months,
        currency=currency,
    )

    return MonthlySpendingResponse(**result)


@router.get(
    "/insights",
    response_model=InsightsResponse,
    summary="Get spending insights summary",
)
def insights(
    user_id: int = Query(..., description="The user's ID"),
    start_date: Optional[str] = Query(
        None, description="Start date in ISO format (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = Query(
        None, description="End date in ISO format (YYYY-MM-DD)"
    ),
    db: Session = Depends(get_db_session),
) -> InsightsResponse:
    """
    Get a summary view with key metrics combining spending by category and monthly trends.

    Returns high-level metrics including total spending, top categories, and monthly trends.
    """
    # Parse dates if provided
    start_dt = parse_iso_date(start_date) if start_date else None
    end_dt = parse_iso_date(end_date) if end_date else None

    result = get_insights(
        user_id=user_id,
        db=db,
        start_date=start_dt,
        end_date=end_dt,
    )

    return InsightsResponse(**result)
