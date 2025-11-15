"""
Extended view endpoints for Account analytics and reporting.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db_session

from ..services.user_account_service import (
    get_transactions_for_account,
    get_transactions_grouped_by_month,
)
from .account_schemas import AccountTransactionsResponse, MonthGroup

router = APIRouter()


@router.get("/views/transactions_by_month", response_model=List[MonthGroup])
def get_transactions_by_month(
    user_id: int, db: Session = Depends(get_db_session)
) -> List[MonthGroup]:
    """
    Get all transactions grouped by month for a user.
    """

    result = get_transactions_grouped_by_month(user_id=user_id, db=db)

    if result is None:
        raise HTTPException(status_code=404, detail="Account not found")

    # Convert plain dicts from the service into Pydantic model instances
    # so the endpoint returns typed objects instead of raw dicts.
    return [MonthGroup(**m) for m in result]


@router.get("/views/transactions", response_model=AccountTransactionsResponse)
def get_account_transactions(
    account_id: int, user_id: int, db: Session = Depends(get_db_session)
) -> AccountTransactionsResponse:
    """
    Get all transactions and their entries for a specific account.
    """

    result = get_transactions_for_account(account_id=account_id, user_id=user_id, db=db)

    if result is None:
        raise HTTPException(status_code=404, detail="Account not found")

    # Wrap the service dict into the response model so we return a typed object.
    return AccountTransactionsResponse(**result)
