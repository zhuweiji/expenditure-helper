from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uix_user_account_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(
        String, index=True
    )  # Removed unique=True, now unique per user
    account_type: Mapped[str] = mapped_column(
        String, nullable=True
    )  # 'asset', 'liability', 'equity', 'revenue', 'expense'
    balance: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), default=0.0
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="accounts")  # type: ignore  # noqa: F821
    entries: Mapped[list["Entry"]] = relationship(back_populates="account")  # type: ignore  # noqa: F821

    # this should be moved out of ledger and put into a join table or something so that ledger can remain pure
    statements: Mapped[list["Statement"]] = relationship(back_populates="account")  # type: ignore  # noqa: F821
