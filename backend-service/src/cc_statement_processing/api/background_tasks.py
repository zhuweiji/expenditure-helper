"""
Background task handlers for statement processing.
"""

from src.common.logger import get_logger
from src.database import get_db_session

from ..models import Statement, StatementProcessing
from ..repositories.statement_repository import (
    StatementProcessingRepository,
    StatementRepository,
)
from .statement_utilities import process_pdf_with_ai

log = get_logger(__name__)


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

    # Create a new database session for the background task
    db = next(get_db_session())

    try:
        # Process the PDF and extract CSV
        csv_output = await process_pdf_with_ai(pdf_content, statement_id)

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
