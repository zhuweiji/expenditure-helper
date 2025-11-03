from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    description: Mapped[str] = mapped_column(String)
    transaction_date: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    reference: Mapped[Optional[str]] = mapped_column(
        String, default=None
    )  # Optional reference number

    # Relationships
    user: Mapped["User"] = relationship(back_populates="transactions")  # type: ignore  # noqa: F821
    entries: Mapped[list["Entry"]] = relationship(
        back_populates="transaction", cascade="all, delete-orphan"
    )
