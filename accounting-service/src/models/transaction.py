from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    transaction_date = Column(DateTime, default=datetime.utcnow)
    reference = Column(String)  # Optional reference number

    entries = relationship(
        "Entry", back_populates="transaction", cascade="all, delete-orphan"
    )
