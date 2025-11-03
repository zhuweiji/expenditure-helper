from datetime import datetime

from sqlalchemy.orm import Session

from ..models import ProcessingStatus, Statement, StatementProcessing


class StatementRepository:
    """Repository for Statement database operations"""

    @staticmethod
    def create_statement(
        filename: str, saved_path: str, file_hash: str, db: Session
    ) -> Statement:
        """
        Create and persist a new statement record in the database.

        Args:
            filename: Original filename of the statement
            saved_path: Path where the file is saved
            file_hash: SHA256 hash of the file content
            db: Database session

        Returns:
            The created Statement object
        """
        statement = Statement(
            filename=filename,
            saved_path=saved_path,
            file_hash=file_hash,
            created_at=datetime.utcnow(),
        )
        db.add(statement)
        db.commit()
        db.refresh(statement)
        return statement

    @staticmethod
    def get_statement_by_hash(file_hash: str, db: Session) -> Statement | None:
        """
        Get a statement by its file hash.

        Args:
            file_hash: SHA256 hash of the file content
            db: Database session

        Returns:
            The Statement object or None if not found
        """
        return db.query(Statement).filter(Statement.file_hash == file_hash).first()

    @staticmethod
    def get_statement_by_id(statement_id: int, db: Session) -> Statement | None:
        """
        Get a statement by its ID.

        Args:
            statement_id: ID of the statement to retrieve
            db: Database session

        Returns:
            The Statement object or None if not found
        """
        return db.query(Statement).filter(Statement.id == statement_id).first()

    @staticmethod
    def list_statements(
        db: Session, skip: int = 0, limit: int = 100
    ) -> list[Statement]:
        """
        Get a list of all statements.

        Args:
            db: Database session
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            List of Statement objects
        """
        return (
            db.query(Statement)
            .order_by(Statement.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_statement_csv_output(
        statement: Statement, csv_output: str, db: Session
    ) -> None:
        """
        Update the CSV output for a statement.

        Args:
            statement: The statement record to update
            csv_output: The CSV output from processing
            db: Database session
        """
        statement.csv_output = csv_output
        db.commit()
        db.refresh(statement)


class StatementProcessingRepository:
    """Repository for StatementProcessing database operations"""

    @staticmethod
    def create_processing_record(statement_id: int, db: Session) -> StatementProcessing:
        """
        Create and persist a new processing record for a statement.

        Args:
            statement_id: ID of the statement to process
            db: Database session

        Returns:
            The created StatementProcessing object
        """
        processing_record = StatementProcessing(
            statement_id=statement_id,
            status=ProcessingStatus.NOT_STARTED,
            created_at=datetime.utcnow(),
        )
        db.add(processing_record)
        db.commit()
        db.refresh(processing_record)
        return processing_record

    @staticmethod
    def update_to_in_progress(
        processing_record: StatementProcessing, db: Session
    ) -> None:
        """
        Update the processing record status to IN_PROGRESS.

        Args:
            processing_record: The processing record to update
            db: Database session
        """
        processing_record.status = ProcessingStatus.IN_PROGRESS
        processing_record.started_at = datetime.utcnow()
        db.commit()

    @staticmethod
    def update_to_completed(
        processing_record: StatementProcessing, db: Session
    ) -> None:
        """
        Update the processing record status to COMPLETED.

        Args:
            processing_record: The processing record to update
            db: Database session
        """
        processing_record.status = ProcessingStatus.COMPLETED
        processing_record.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(processing_record)

    @staticmethod
    def update_to_errored(
        processing_record: StatementProcessing | None,
        error_message: str,
        db: Session,
    ) -> None:
        """
        Update processing record with error status and message.

        Args:
            processing_record: The processing record to update (may be None)
            error_message: The error message to store
            db: Database session
        """
        if processing_record:
            processing_record.status = ProcessingStatus.ERRORED
            processing_record.error_message = error_message
            processing_record.completed_at = datetime.utcnow()
            db.commit()

    @staticmethod
    def get_processing_by_id(
        processing_id: int, db: Session
    ) -> StatementProcessing | None:
        """
        Get a processing record by its ID.

        Args:
            processing_id: ID of the processing record to retrieve
            db: Database session

        Returns:
            The StatementProcessing object or None if not found
        """
        return (
            db.query(StatementProcessing)
            .filter(StatementProcessing.id == processing_id)
            .first()
        )

    @staticmethod
    def list_processing_records(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
    ) -> list[StatementProcessing]:
        """
        Get a list of all statement processing records.

        Args:
            db: Database session
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            status: Optional filter by processing status

        Returns:
            List of StatementProcessing objects
        """
        query = db.query(StatementProcessing)

        if status:
            query = query.filter(StatementProcessing.status == status)

        return (
            query.order_by(StatementProcessing.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
