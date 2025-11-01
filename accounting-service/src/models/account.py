from sqlalchemy import Column, Integer, Numeric, String
from sqlalchemy.orm import relationship

from ..database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    account_type = Column(
        String, nullable=False
    )  # 'asset', 'liability', 'equity', 'revenue', 'expense'
    balance = Column(Numeric(precision=10, scale=2), default=0.0)

    entries = relationship("Entry", back_populates="account")
