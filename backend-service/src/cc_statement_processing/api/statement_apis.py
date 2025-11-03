"""
API endpoints for credit card statement processing.
"""

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from src.common.logger import get_logger
from src.database import get_db_session

from ..models import ProcessingStatus, Statement, StatementProcessing
from ..repositories.statement_repository import (
    StatementProcessingRepository,
    StatementRepository,
)
from .background_tasks import process_statement_background
from .statement_schemas import (
    ProcessingDetailResponse,
    ProcessingListResponse,
    StatementDetailResponse,
    StatementListResponse,
    StatementProcessResponse,
)
from .statement_utilities import (
    cleanup_file,
    compute_file_hash,
    filter_duplicate_file_uploads,
    generate_safe_filename,
    save_uploaded_file,
    validate_pdf_file,
)

router = APIRouter()

log = get_logger(__name__)


@router.post("/upload", response_model=StatementProcessResponse)
async def upload_and_process_statement(
    user_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Credit card statement PDF file"),
    db: Session = Depends(get_db_session),
):
    """
    Upload a credit card statement PDF, save it locally, and process it with ChatGPT
    to extract transaction data as CSV.

    Args:
        user_id: ID of the user uploading the statement
        background_tasks: FastAPI background tasks manager
        file: PDF file to upload
        db: Database session

    Returns:
        StatementProcessResponse with the CSV output and file information
    """
    log.info(f"Received upload request for file: {file.filename} from user: {user_id}")

    # Validate file type
    validate_pdf_file(file)

    # Initialize tracking variables
    file_path = None
    statement = None
    processing_record = None

    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a filename")

    file_data = await file.read()

    if existing_processing_id := filter_duplicate_file_uploads(file_data, user_id, db):
        return StatementProcessResponse(id=existing_processing_id)

    try:
        safe_filename, file_path = generate_safe_filename(file.filename)
        log.info(f"Saving file to: {file_path}")

        # Create database records
        statement = StatementRepository.create_statement(
            filename=file.filename,
            saved_path=str(file_path),
            file_hash=compute_file_hash(file_data),
            user_id=user_id,
            db=db,
        )
        processing_record = StatementProcessingRepository.create_processing_record(
            statement_id=statement.id,
            db=db,
        )
        log.info(
            f"Created statement record with ID: {statement.id} for user: {user_id}"
        )
        log.info(f"Created processing record with ID: {processing_record.id}")

        pdf_content = await save_uploaded_file(file_data, file_path)

        StatementProcessingRepository.update_to_in_progress(processing_record, db)
        log.info(
            f"Queued processing for statement (ID: {processing_record.statement_id})"
        )

        background_tasks.add_task(
            process_statement_background,
            statement.id,
            processing_record.id,
            pdf_content,
        )

        return StatementProcessResponse(id=processing_record.id)

    except ValueError as e:
        log.error(f"Value error processing file {file.filename}: {str(e)}")
        if processing_record:
            StatementProcessingRepository.update_to_errored(
                processing_record, str(e), db
            )
        cleanup_file(file_path)
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
        cleanup_file(file_path)
        raise HTTPException(
            status_code=500, detail=f"Error processing statement: {str(e)}"
        )


@router.get("/", response_model=list[StatementListResponse])
async def list_statements(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_session),
):
    """
    Get a list of all statements for a specific user.

    Args:
        user_id: ID of the user whose statements to retrieve
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List of statements for the user
    """
    log.info(
        f"Fetching statements list for user {user_id} (skip={skip}, limit={limit})"
    )

    statements = (
        db.query(Statement)
        .filter(Statement.user_id == user_id)
        .order_by(Statement.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    log.info(f"Retrieved {len(statements)} statements for user {user_id}")

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
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    db: Session = Depends(get_db_session),
):
    """
    Get a list of all statement processing records for a specific user.

    Args:
        user_id: ID of the user whose processing records to retrieve
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        status: Optional filter by processing status
        db: Database session

    Returns:
        List of processing records for the user
    """
    log.info(
        f"Fetching processing records list for user {user_id} (skip={skip}, limit={limit}, status={status})"
    )

    query = (
        db.query(StatementProcessing)
        .join(Statement)
        .filter(Statement.user_id == user_id)
    )

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

    log.info(
        f"Retrieved {len(processing_records)} processing records for user {user_id}"
    )

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
    user_id: int,
    db: Session = Depends(get_db_session),
):
    """
    Get detailed information about a specific statement.

    Args:
        statement_id: ID of the statement to retrieve
        user_id: ID of the user requesting the statement
        db: Database session

    Returns:
        Statement details including CSV output
    """
    log.info(f"Fetching statement detail for ID: {statement_id}")

    statement = (
        db.query(Statement)
        .filter(Statement.id == statement_id, Statement.user_id == user_id)
        .first()
    )

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
    user_id: int,
    db: Session = Depends(get_db_session),
):
    """
    Get detailed information about a specific processing record.

    Args:
        processing_id: ID of the processing record to retrieve
        user_id: ID of the user requesting the processing record
        db: Database session

    Returns:
        Processing record details including error messages
    """
    log.info(f"Fetching processing detail for ID: {processing_id}")

    processing = (
        db.query(StatementProcessing)
        .join(Statement)
        .filter(StatementProcessing.id == processing_id, Statement.user_id == user_id)
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
    user_id: int,
    db: Session = Depends(get_db_session),
):
    """
    Delete a statement and its associated processing record.
    Also deletes the physical PDF file from disk.

    Args:
        statement_id: ID of the statement to delete
        user_id: ID of the user requesting the deletion
        db: Database session

    Returns:
        Success message
    """
    log.info(f"Attempting to delete statement ID: {statement_id}")

    statement = (
        db.query(Statement)
        .filter(Statement.id == statement_id, Statement.user_id == user_id)
        .first()
    )

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
    user_id: int,
    db: Session = Depends(get_db_session),
):
    """
    Delete a processing record. Can only be deleted if status is 'errored'.

    Args:
        processing_id: ID of the processing record to delete
        user_id: ID of the user requesting the deletion
        db: Database session

    Returns:
        Success message
    """
    log.info(f"Attempting to delete processing record ID: {processing_id}")

    processing = (
        db.query(StatementProcessing)
        .join(Statement)
        .filter(StatementProcessing.id == processing_id, Statement.user_id == user_id)
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
