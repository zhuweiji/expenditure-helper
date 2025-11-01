from pydantic import BaseModel
from datetime import datetime

class Entry(BaseModel):
    id: int
    account_id: int
    amount: float
    timestamp: datetime

    class Config:
        orm_mode = True