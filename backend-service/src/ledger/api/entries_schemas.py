from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EntryBase(BaseModel):
    account_id: int
    amount: float
    entry_type: str
    description: Optional[str] = None


class EntryCreate(EntryBase):
    timestamp: Optional[datetime] = None


class EntryUpdate(EntryBase):
    pass


class Entry(BaseModel):
    id: int
    account_id: int
    amount: float
    entry_type: str
    description: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True
