"""
Pydantic schemas for statement API request/response models.
"""

from pydantic import BaseModel


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
