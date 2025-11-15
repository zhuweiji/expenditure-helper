"""
Helper functions and dependencies for statement processing.
"""

import hashlib
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from src.common.logger import get_logger
from src.common.project_paths import cc_statement_dir
from src.database import get_db_session

from ..models import Statement, StatementProcessing
from ..repositories.statement_repository import (
    StatementProcessingRepository,
    StatementRepository,
)
from ..services.cc_statement_processor import CreditCardStatementProcessor

log = get_logger(__name__)


def compute_file_hash(content: bytes) -> str:
    """
    Compute SHA256 hash of file content.

    Args:
        content: The file content as bytes

    Returns:
        Hexadecimal string representation of the hash
    """
    return hashlib.sha256(content).hexdigest()


def validate_pdf_file(file: UploadFile) -> None:
    """
    Validate that the uploaded file is a PDF.

    Args:
        file: The uploaded file to validate

    Raises:
        HTTPException: If the file is not a PDF
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        log.warning(f"Invalid file type uploaded: {file.filename}")
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")


def generate_safe_filename(original_filename: str) -> tuple[str, Path]:
    """
    Generate a unique, timestamped filename and full file path.

    Args:
        original_filename: The original filename from the upload

    Returns:
        Tuple of (safe_filename, full_file_path)
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{original_filename}"
    file_path = cc_statement_dir / safe_filename
    return safe_filename, file_path


async def save_uploaded_file(file_data: bytes, file_path: Path) -> bytes:
    """
    Read and save the uploaded file to disk.

    Args:
        file_data: The file content as bytes
        file_path: Destination path for the file

    Returns:
        The file content as bytes
    """
    log.debug(f"Read {len(file_data)} bytes from uploaded file")

    with open(file_path, "wb") as f:
        f.write(file_data)

    log.info(f"Successfully saved file to disk: {file_path.name}")
    return file_data


async def process_statement_background(
    statement_id: int, processing_id: int, pdf_content: bytes
):
    """
    Background task to process the statement PDF and update the database.

    Args:
        statement_id: ID of the statement
        processing_id: ID of the processing record
        pdf_content: The PDF file content as bytes
    """
    log.info(f"Background processing started for statement ID: {statement_id}")

    processor = CreditCardStatementProcessor()

    # Create a new database session for the background task
    db = next(get_db_session())

    try:
        # Process the PDF and extract CSV
        csv_output = await processor.process_pdf_statement_async(pdf_content)

        # Update records with success
        statement = db.query(Statement).filter(Statement.id == statement_id).first()
        processing_record = (
            db.query(StatementProcessing)
            .filter(StatementProcessing.id == processing_id)
            .first()
        )

        if statement and processing_record:
            StatementRepository.update_statement_csv_output(statement, csv_output, db)
            StatementProcessingRepository.update_to_completed(processing_record, db)
            log.info(
                f"Completed background processing for statement (ID: {statement_id})"
            )
        else:
            log.warning(
                f"Statement or processing record not found for ID: {statement_id}"
            )

    except Exception as e:
        # Log and update the processing record with error
        log.error(
            f"Error in background processing of statement ID {statement_id}: {str(e)}",
            exc_info=True,
        )
        processing_record = (
            db.query(StatementProcessing)
            .filter(StatementProcessing.id == processing_id)
            .first()
        )
        if processing_record:
            StatementProcessingRepository.update_to_errored(
                processing_record, str(e), db
            )

    finally:
        # Close the database session
        db.close()


def cleanup_file(file_path: Path | None) -> None:
    """
    Clean up the uploaded file if it exists.

    Args:
        file_path: Path to the file to delete
    """
    if file_path and file_path.exists():
        file_path.unlink()
        log.info(f"Cleaned up file after processing error: {file_path}")


def filter_duplicate_file_uploads(
    pdf_content: bytes, user_id: int, db: Session
) -> int | None:
    """
    Check for duplicate file uploads for a specific user based on file hash.

    Args:
        pdf_content: The PDF file content as bytes
        user_id: ID of the user uploading the file
        db: Database session

    Returns:
        Processing ID if duplicate found, None otherwise
    """
    # Check for duplicate processing based on file hash
    file_hash = compute_file_hash(pdf_content)
    log.info(f"Computed file hash: {file_hash}")

    existing_statement = (
        db.query(Statement)
        .filter(Statement.file_hash == file_hash, Statement.user_id == user_id)
        .first()
    )

    if existing_statement:
        log.info(
            f"Duplicate file detected for user {user_id}. Existing statement: {existing_statement.id}"
        )
        assert existing_statement.processing is not None, (
            "Processing record should exist for duplicate statement"
        )
        return existing_statement.processing.id
    return None
