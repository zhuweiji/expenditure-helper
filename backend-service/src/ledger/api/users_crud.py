"""
CRUD endpoints for User operations.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from src.database import get_db_session

from ..models.user import User
from ..services.user_account_service import create_default_accounts_for_user
from .user_schemas import UserCreateRequest, UserResponse, UserUpdateRequest

router = APIRouter()


@router.get("", response_model=list[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = True,
    db: Session = Depends(get_db_session),
):
    """
    List all users with optional filtering by active status.
    """
    query = db.query(User)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    users = query.offset(skip).limit(limit).all()
    return users


@router.post("", response_model=UserResponse, status_code=201)
def create_user(user: UserCreateRequest, db: Session = Depends(get_db_session)):
    """
    Create a new user and automatically set up default accounts for double-entry bookkeeping.

    Default accounts created:
    - Assets: Cash, Bank Account, Accounts Receivable
    - Liabilities: Accounts Payable, Credit Card
    - Equity: Owner's Equity, Retained Earnings
    - Revenue: Sales Revenue, Other Income
    - Expenses: General Expenses, Food & Dining, Transportation, Utilities
    """
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=True,
    )

    try:
        db.add(db_user)
        db.flush()  # Flush to get the user ID before creating accounts

        # Create default accounts for the new user
        create_default_accounts_for_user(db, db_user.id)

        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        if "username" in str(e.orig):
            raise HTTPException(status_code=400, detail="Username already exists")
        elif "email" in str(e.orig):
            raise HTTPException(status_code=400, detail="Email already exists")
        else:
            raise HTTPException(status_code=400, detail="Failed to create user")


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db_session)):
    """
    Get a specific user by ID.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/username/{username}", response_model=UserResponse)
def get_user_by_username(username: str, db: Session = Depends(get_db_session)):
    """
    Get a specific user by username.
    """
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/email/{email_address}", response_model=UserResponse)
def get_user_by_email_address(
    email_address: str, db: Session = Depends(get_db_session)
):
    """
    Get a specific user by email address.
    """
    user = db.query(User).filter(User.email == email_address).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdateRequest,
    db: Session = Depends(get_db_session),
):
    """
    Update a user's details. Username cannot be changed.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Update only provided fields
    if user_update.email is not None:
        db_user.email = user_update.email
    if user_update.full_name is not None:
        db_user.full_name = user_update.full_name
    if user_update.is_active is not None:
        db_user.is_active = user_update.is_active
    if user_update.timezone is not None:
        db_user.timezone = user_update.timezone
    if user_update.currency is not None:
        db_user.currency = user_update.currency

    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db_session)):
    """
    Delete a user and all their associated data (accounts, transactions, statements).
    This is a hard delete due to cascade rules defined in the model.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return None
