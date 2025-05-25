"""
Pydantic models for the upload service API.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
import datetime


class UploadStatus(str, Enum):
    """Enum for upload status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class UploadResponse(BaseModel):
    """Response model for upload endpoints."""
    id: str = Field(..., description="Unique identifier for the upload")
    filename: str = Field(..., description="Name of the uploaded file")
    status: UploadStatus = Field(..., description="Current status of the upload")
    message: str = Field(..., description="Status message")
    created_at: Optional[datetime.datetime] = Field(
        default_factory=datetime.datetime.now,
        description="Timestamp when the upload was created"
    )
    processed: int = Field(0, description="Number of records processed successfully")
    skipped: int = Field(0, description="Number of records skipped (e.g., duplicates)")
    failed: int = Field(0, description="Number of records with errors")
    total_records: int = Field(0, description="Total number of records in the file")
    error_details: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Details of errors encountered"
    )

    class Config:
        from_attributes = True


class UploadStatsResponse(BaseModel):
    """Response model for upload statistics."""
    total_uploads: int = Field(..., description="Total number of uploads")
    successful_uploads: int = Field(..., description="Number of successful uploads")
    failed_uploads: int = Field(..., description="Number of failed uploads")
    processing_uploads: int = Field(..., description="Number of uploads in progress")
    records_processed: int = Field(..., description="Total number of records processed")
    most_recent_upload: Optional[datetime.datetime] = Field(
        None,
        description="Timestamp of the most recent upload"
    )