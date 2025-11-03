from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base


class Entry(Base):
    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"))
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    # Use 'debit' or 'credit' to indicate the side of the entry
    entry_type: Mapped[str] = mapped_column(String)  # 'debit' or 'credit'
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2))
    description: Mapped[Optional[str]] = mapped_column(String, default=None)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    account: Mapped["Account"] = relationship(back_populates="entries")  # type: ignore
    transaction: Mapped["Transaction"] = relationship(back_populates="entries")  # type: ignore
