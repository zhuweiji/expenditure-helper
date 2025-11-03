from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base


class ProcessingStatus(str, Enum):
    """Enum for statement processing status"""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERRORED = "errored"


class Statement(Base):
    """DB model for a completed credit card statement"""

    __tablename__ = "statements"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String, index=True)
    saved_path: Mapped[str] = mapped_column(String)
    file_hash: Mapped[str] = mapped_column(String, index=True, unique=True)
    account_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("accounts.id"), nullable=True, index=True
    )
    csv_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    account: Mapped[Optional["Account"]] = relationship(back_populates="statements")  # type: ignore  # noqa: F821
    processing: Mapped[Optional["StatementProcessing"]] = relationship(
        back_populates="statement", uselist=False
    )


class StatementProcessing(Base):
    """DB model for tracking statement processing jobs"""

    __tablename__ = "statement_processing"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    statement_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("statements.id"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(
        String, default=ProcessingStatus.NOT_STARTED, index=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationship to Statement
    statement: Mapped[Optional["Statement"]] = relationship(back_populates="processing")
