import hashlib
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.common.logger import get_logger
from src.database import get_db_session

from ..models import ProcessingStatus, Statement, StatementProcessing
from ..repositories.statement_repository import (
    StatementProcessingRepository,
    StatementRepository,
)
from ..services.cc_statement_processor import CreditCardStatementProcessor

router = APIRouter()

# Define the data folder path
DATA_FOLDER = Path(__file__).parent.parent.parent / "data" / "statements"
DATA_FOLDER.mkdir(parents=True, exist_ok=True)

log = get_logger(__name__)


class StatementProcessResponse(BaseModel):
    """Response model for statement processing"""

    id: int


class StatementDetailResponse(BaseModel):
    """Response model for statement detail"""

    id: int
    filename: str
    saved_path: str
    account_id: int | None
    csv_output: str | None
    created_at: str
    file_hash: str

    class Config:
        from_attributes = True


class StatementListResponse(BaseModel):
    """Response model for statement list"""

    id: int
    filename: str
    saved_path: str
    account_id: int | None
    created_at: str
    file_hash: str

    class Config:
        from_attributes = True


class ProcessingDetailResponse(BaseModel):
    """Response model for statement processing detail"""

    id: int
    statement_id: int | None
    status: str
    error_message: str | None
    created_at: str
    started_at: str | None
    completed_at: str | None

    class Config:
        from_attributes = True


class ProcessingListResponse(BaseModel):
    """Response model for statement processing list"""

    id: int
    statement_id: int | None
    status: str
    created_at: str
    completed_at: str | None

    class Config:
        from_attributes = True


def _compute_file_hash(content: bytes) -> str:
    """
    Compute SHA256 hash of file content.

    Args:
        content: The file content as bytes

    Returns:
        Hexadecimal string representation of the hash
    """
    return hashlib.sha256(content).hexdigest()


def _validate_pdf_file(file: UploadFile) -> None:
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


def _generate_safe_filename(original_filename: str) -> tuple[str, Path]:
    """
    Generate a unique, timestamped filename and full file path.

    Args:
        original_filename: The original filename from the upload

    Returns:
        Tuple of (safe_filename, full_file_path)
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{original_filename}"
    file_path = DATA_FOLDER / safe_filename
    return safe_filename, file_path


async def _save_uploaded_file(file_data: bytes, file_path: Path) -> bytes:
    """
    Read and save the uploaded file to disk.

    Args:
        file: The uploaded file
        file_path: Destination path for the file

    Returns:
        The file content as bytes
    """
    log.debug(f"Read {len(file_data)} bytes from uploaded file")

    with open(file_path, "wb") as f:
        f.write(file_data)

    log.info(f"Successfully saved file to disk: {file_path.name}")
    return file_data


async def _process_pdf_with_ai(pdf_content: bytes, statement_id: int) -> str:
    """
    Process PDF content using AI to extract transaction data.

    Args:
        pdf_content: The PDF file content as bytes
        statement_id: ID of the statement being processed

    Returns:
        CSV output from the processing
    """
    processor = CreditCardStatementProcessor()
    log.debug(f"Initialized PDF processor for statement ID: {statement_id}")
    csv_output = await processor.process_pdf_statement_async(pdf_content)
    log.info(f"Successfully processed PDF statement (ID: {statement_id})")
    return csv_output


def _cleanup_file(file_path: Path | None) -> None:
    """
    Clean up the uploaded file if it exists.

    Args:
        file_path: Path to the file to delete
    """
    if file_path and file_path.exists():
        file_path.unlink()
        log.info(f"Cleaned up file after processing error: {file_path}")


def _filter_duplicate_file_uploads(pdf_content: bytes, db: Session) -> int | None:
    # Check for duplicate processing based on file hash
    file_hash = _compute_file_hash(pdf_content)
    log.info(f"Computed file hash: {file_hash}")

    existing_statement = (
        db.query(Statement).filter(Statement.file_hash == file_hash).first()
    )

    if existing_statement:
        log.info(
            f"Duplicate file detected. Existing statement: {existing_statement.id}"
        )
        assert existing_statement.processing is not None, (
            "Processing record should exist for duplicate statement"
        )
        return existing_statement.processing.id


@router.post("/upload", response_model=StatementProcessResponse)
async def upload_and_process_statement(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Credit card statement PDF file"),
    db: Session = Depends(get_db_session),
):
    """
    Upload a credit card statement PDF, save it locally, and process it with ChatGPT
    to extract transaction data as CSV.

    Args:
        background_tasks: FastAPI background tasks manager
        file: PDF file to upload
        db: Database session

    Returns:
        StatementProcessResponse with the CSV output and file information
    """
    log.info(f"Received upload request for file: {file.filename}")

    # Validate file type
    _validate_pdf_file(file)

    # Initialize tracking variables
    file_path = None
    statement = None
    processing_record = None

    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a filename")

    file_data = await file.read()

    if existing_processing_id := _filter_duplicate_file_uploads(file_data, db):
        return StatementProcessResponse(id=existing_processing_id)

    try:
        # Generate safe filename and path
        safe_filename, file_path = _generate_safe_filename(file.filename)
        log.info(f"Saving file to: {file_path}")

        # Create database records
        statement = StatementRepository.create_statement(
            filename=file.filename,
            saved_path=str(file_path),
            db=db,
            file_hash=_compute_file_hash(file_data),
        )
        processing_record = StatementProcessingRepository.create_processing_record(
            statement_id=statement.id,
            db=db,
        )
        log.info(f"Created statement record with ID: {statement.id}")
        log.info(f"Created processing record with ID: {processing_record.id}")

        # Save file and get content
        pdf_content = await _save_uploaded_file(file_data, file_path)

        # Update status to in progress
        StatementProcessingRepository.update_to_in_progress(processing_record, db)
        log.info(
            f"Queued processing for statement (ID: {processing_record.statement_id})"
        )

        # Process the statement in the background
        background_tasks.add_task(
            _process_statement_background,
            statement.id,
            processing_record.id,
            pdf_content,
        )

        # Return response immediately
        return StatementProcessResponse(id=processing_record.id)

    except ValueError as e:
        log.error(f"Value error processing file {file.filename}: {str(e)}")
        if processing_record:
            StatementProcessingRepository.update_to_errored(
                processing_record, str(e), db
            )
        _cleanup_file(file_path)
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        # Update record with error
        log.error(
            f"Unexpected error processing file {file.filename}: {str(e)}", exc_info=True
        )
        if processing_record:
            StatementProcessingRepository.update_to_errored(
                processing_record, str(e), db
            )
        _cleanup_file(file_path)
        raise HTTPException(
            status_code=500, detail=f"Error processing statement: {str(e)}"
        )


async def _process_statement_background(
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
        csv_output = await _process_pdf_with_ai(pdf_content, statement_id)

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


@router.get("/", response_model=list[StatementListResponse])
async def list_statements(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_session),
):
    """
    Get a list of all statements.

    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List of statements
    """
    log.info(f"Fetching statements list (skip={skip}, limit={limit})")

    statements = (
        db.query(Statement)
        .order_by(Statement.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    log.info(f"Retrieved {len(statements)} statements")

    return [
        StatementListResponse(
            id=stmt.id,
            filename=stmt.filename,
            saved_path=stmt.saved_path,
            account_id=stmt.account_id,
            created_at=stmt.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            file_hash=stmt.file_hash,
        )
        for stmt in statements
    ]


@router.get("/processing", response_model=list[ProcessingListResponse])
async def list_processing_records(
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    db: Session = Depends(get_db_session),
):
    """
    Get a list of all statement processing records.

    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        status: Optional filter by processing status
        db: Database session

    Returns:
        List of processing records
    """
    log.info(
        f"Fetching processing records list (skip={skip}, limit={limit}, status={status})"
    )

    query = db.query(StatementProcessing)

    if status:
        try:
            # Validate status enum value
            ProcessingStatus(status)
            query = query.filter(StatementProcessing.status == status)
        except ValueError:
            log.warning(f"Invalid status filter: {status}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join([s.value for s in ProcessingStatus])}",
            )

    processing_records = (
        query.order_by(StatementProcessing.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    log.info(f"Retrieved {len(processing_records)} processing records")

    return [
        ProcessingListResponse(
            id=rec.id,
            statement_id=rec.statement_id,
            status=rec.status,
            created_at=rec.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            completed_at=rec.completed_at.strftime("%Y-%m-%d %H:%M:%S")
            if rec.completed_at
            else None,
        )
        for rec in processing_records
    ]


@router.get("/{statement_id}", response_model=StatementDetailResponse)
async def get_statement_detail(
    statement_id: int,
    db: Session = Depends(get_db_session),
):
    """
    Get detailed information about a specific statement.

    Args:
        statement_id: ID of the statement to retrieve
        db: Database session

    Returns:
        Statement details including CSV output
    """
    log.info(f"Fetching statement detail for ID: {statement_id}")

    statement = db.query(Statement).filter(Statement.id == statement_id).first()

    if not statement:
        log.warning(f"Statement not found: {statement_id}")
        raise HTTPException(status_code=404, detail="Statement not found")

    log.info(f"Retrieved statement detail for ID: {statement_id}")

    return StatementDetailResponse(
        id=statement.id,
        filename=statement.filename,
        saved_path=statement.saved_path,
        account_id=statement.account_id,
        csv_output=statement.csv_output,
        created_at=statement.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        file_hash=statement.file_hash,
    )


@router.get("/processing/{processing_id}", response_model=ProcessingDetailResponse)
async def get_processing_detail(
    processing_id: int,
    db: Session = Depends(get_db_session),
):
    """
    Get detailed information about a specific processing record.

    Args:
        processing_id: ID of the processing record to retrieve
        db: Database session

    Returns:
        Processing record details including error messages
    """
    log.info(f"Fetching processing detail for ID: {processing_id}")

    processing = (
        db.query(StatementProcessing)
        .filter(StatementProcessing.id == processing_id)
        .first()
    )

    if not processing:
        log.warning(f"Processing record not found: {processing_id}")
        raise HTTPException(status_code=404, detail="Processing record not found")

    log.info(f"Retrieved processing detail for ID: {processing_id}")

    return ProcessingDetailResponse(
        id=processing.id,
        statement_id=processing.statement_id,
        status=processing.status,
        error_message=processing.error_message,
        created_at=processing.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        started_at=processing.started_at.strftime("%Y-%m-%d %H:%M:%S")
        if processing.started_at
        else None,
        completed_at=processing.completed_at.strftime("%Y-%m-%d %H:%M:%S")
        if processing.completed_at
        else None,
    )


@router.delete("/{statement_id}")
async def delete_statement(
    statement_id: int,
    db: Session = Depends(get_db_session),
):
    """
    Delete a statement and its associated processing record.
    Also deletes the physical PDF file from disk.

    Args:
        statement_id: ID of the statement to delete
        db: Database session

    Returns:
        Success message
    """
    log.info(f"Attempting to delete statement ID: {statement_id}")

    statement = db.query(Statement).filter(Statement.id == statement_id).first()

    if not statement:
        log.warning(f"Statement not found: {statement_id}")
        raise HTTPException(status_code=404, detail="Statement not found")

    # Delete the associated processing record first (if exists)
    if statement.processing:
        db.delete(statement.processing)
        log.info(f"Deleted processing record for statement ID: {statement_id}")

    # Delete the physical file
    file_path = Path(statement.saved_path)
    if file_path.exists():
        file_path.unlink()
        log.info(f"Deleted physical file: {file_path}")
    else:
        log.warning(f"Physical file not found: {file_path}")

    # Delete the statement record
    db.delete(statement)
    db.commit()

    log.info(f"Successfully deleted statement ID: {statement_id}")
    return {"message": f"Statement {statement_id} deleted successfully"}


@router.delete("/processing/{processing_id}")
async def delete_processing_record(
    processing_id: int,
    db: Session = Depends(get_db_session),
):
    """
    Delete a processing record. Can only be deleted if status is 'errored'.

    Args:
        processing_id: ID of the processing record to delete
        db: Database session

    Returns:
        Success message
    """
    log.info(f"Attempting to delete processing record ID: {processing_id}")

    processing = (
        db.query(StatementProcessing)
        .filter(StatementProcessing.id == processing_id)
        .first()
    )

    if not processing:
        log.warning(f"Processing record not found: {processing_id}")
        raise HTTPException(status_code=404, detail="Processing record not found")

    # Check if the processing record is in errored state
    if processing.status != ProcessingStatus.ERRORED.value:
        log.warning(
            f"Cannot delete processing record {processing_id} with status: {processing.status}"
        )
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete processing record with status '{processing.status}'. Only errored records can be deleted.",
        )

    db.delete(processing)
    db.commit()

    log.info(f"Successfully deleted processing record ID: {processing_id}")
    return {"message": f"Processing record {processing_id} deleted successfully"}
