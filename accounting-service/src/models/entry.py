from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from ..database import Base


class Entry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    # Use 'debit' or 'credit' to indicate the side of the entry
    entry_type = Column(String, nullable=False)  # 'debit' or 'credit'
    amount = Column(Numeric(precision=10, scale=2), nullable=False)
    description = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    account = relationship("Account", back_populates="entries")
    transaction = relationship("Transaction", back_populates="entries")
