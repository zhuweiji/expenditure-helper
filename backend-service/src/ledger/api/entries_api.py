from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.database import get_db_session

from ..models import Entry as EntryModel
from .entries_schemas import Entry, EntryCreate, EntryUpdate

router = APIRouter()


@router.post("/", response_model=Entry, status_code=201)
async def create_entry(entry: EntryCreate, db: Session = Depends(get_db_session)):
    """Create a new entry"""
    db_entry = EntryModel(
        account_id=entry.account_id,
        amount=entry.amount,
        entry_type=entry.entry_type,
        description=entry.description,
        timestamp=datetime.utcnow(),
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


@router.get("/{entry_id}", response_model=Entry)
async def read_entry(entry_id: int, db: Session = Depends(get_db_session)):
    """Retrieve an entry by ID"""
    db_entry = db.query(EntryModel).filter(EntryModel.id == entry_id).first()
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return db_entry


@router.get("/", response_model=List[Entry])
async def list_entries(
    skip: int = 0,
    limit: int = 100,
    account_id: Optional[int] = None,
    db: Session = Depends(get_db_session),
):
    """List all entries with optional filtering by account_id"""
    query = db.query(EntryModel)
    if account_id is not None:
        query = query.filter(EntryModel.account_id == account_id)
    entries = query.offset(skip).limit(limit).all()
    return entries


@router.put("/{entry_id}", response_model=Entry)
async def update_entry(
    entry_id: int, entry: EntryUpdate, db: Session = Depends(get_db_session)
):
    """Update an entry by ID"""
    db_entry = db.query(EntryModel).filter(EntryModel.id == entry_id).first()
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")

    db_entry.account_id = entry.account_id
    db_entry.amount = entry.amount  # type: ignore
    db_entry.entry_type = entry.entry_type
    db_entry.description = entry.description

    db.commit()
    db.refresh(db_entry)
    return db_entry


@router.delete("/{entry_id}", status_code=204)
async def delete_entry(entry_id: int, db: Session = Depends(get_db_session)):
    """Delete an entry by ID"""
    db_entry = db.query(EntryModel).filter(EntryModel.id == entry_id).first()
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")

    db.delete(db_entry)
    db.commit()
    return None
    return None
