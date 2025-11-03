from decimal import Decimal

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    account_type: Mapped[str] = mapped_column(
        String, nullable=True
    )  # 'asset', 'liability', 'equity', 'revenue', 'expense'
    balance: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), default=0.0
    )

    entries: Mapped[list["Entry"]] = relationship(back_populates="account")  # type: ignore  # noqa: F821

    # this should be moved out of ledger and put into a join table or something so that ledger can remain pure
    statements: Mapped[list["Statement"]] = relationship(back_populates="account")  # type: ignore  # noqa: F821
