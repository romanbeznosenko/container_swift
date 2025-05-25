"""
Router for handling SWIFT code file uploads.
"""

import os
import uuid
import shutil
import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Query, status
from fastapi.responses import JSONResponse

from utils.csv_parser import parse_swift_data
from utils.api_client import create_swift_codes_batch, check_api_health
from utils.exceptions import (
    CSVParsingError,
    MissingColumnError,
    InvalidSwiftCodeError,
    DuplicateSwiftCodeError
)
from utils.logger import setup_logger
from api.models.upload import UploadResponse, UploadStatus, UploadStatsResponse

logger = setup_logger("upload_router")

UPLOAD_DIR = os.path.abspath("./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(
    prefix="/api/v1/upload",
    tags=["upload"],
    responses={
        404: {"description": "Not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)

upload_tasks = {}


async def process_csv_file(file_path: str, upload_id: str):
    """
    Background task to process a CSV file containing SWIFT codes,
    validate them, and send them to the main API.
    
    Args:
        file_path: Path to the CSV file
        upload_id: Unique ID for this upload task
    """
    logger.info(f"Starting to process CSV file: {file_path} (ID: {upload_id})")
    
    try:
        upload_tasks[upload_id]["status"] = UploadStatus.PROCESSING
        upload_tasks[upload_id]["message"] = "Processing file..."
        
        is_api_healthy = await check_api_health()
        if not is_api_healthy:
            raise Exception("SWIFT code API is not available")
        
        swift_codes = parse_swift_data(file_path)
        
        upload_tasks[upload_id]["total_records"] = len(swift_codes)
        upload_tasks[upload_id]["message"] = f"Parsed {len(swift_codes)} records. Sending to API..."
        
        result = await create_swift_codes_batch(swift_codes)
        
        upload_tasks[upload_id]["status"] = UploadStatus.COMPLETED
        upload_tasks[upload_id]["processed"] = result["successful"]
        upload_tasks[upload_id]["skipped"] = result["skipped"]
        upload_tasks[upload_id]["failed"] = result["failed"]
        upload_tasks[upload_id]["message"] = (
            f"Upload complete. {result['successful']} records created, "
            f"{result['skipped']} skipped, {result['failed']} failed."
        )
        upload_tasks[upload_id]["error_details"] = result["errors"]
        
        logger.info(f"CSV processing complete for upload {upload_id}: "
                   f"{result['successful']} created, {result['skipped']} skipped, "
                   f"{result['failed']} failed")
        
    except MissingColumnError as e:
        logger.error(f"Missing column error: {str(e)}")
        upload_tasks[upload_id]["status"] = UploadStatus.FAILED
        upload_tasks[upload_id]["message"] = f"Missing column: {e.column_name}"
        
    except InvalidSwiftCodeError as e:
        logger.error(f"Invalid SWIFT code error: {str(e)}")
        upload_tasks[upload_id]["status"] = UploadStatus.FAILED
        upload_tasks[upload_id]["message"] = str(e)
        
    except DuplicateSwiftCodeError as e:
        logger.error(f"Duplicate SWIFT code error: {str(e)}")
        upload_tasks[upload_id]["status"] = UploadStatus.FAILED
        upload_tasks[upload_id]["message"] = str(e)
        
    except CSVParsingError as e:
        logger.error(f"CSV parsing error: {str(e)}")
        upload_tasks[upload_id]["status"] = UploadStatus.FAILED
        upload_tasks[upload_id]["message"] = f"Error parsing CSV: {str(e)}"
        
    except Exception as e:
        logger.error(f"Error processing CSV file: {str(e)}")
        upload_tasks[upload_id]["status"] = UploadStatus.FAILED
        upload_tasks[upload_id]["message"] = f"Error processing file: {str(e)}"
        
    finally:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Removed temporary file: {file_path}")
        except Exception as e:
            logger.error(f"Error removing temporary file: {str(e)}")


@router.post("/", response_model=UploadResponse)
async def upload_swift_codes_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """
    Upload a CSV file containing SWIFT codes for processing.
    
    The file will be processed asynchronously in the background.
    You can check the status of the processing using the returned upload ID.
    
    Args:
        background_tasks: FastAPI BackgroundTasks
        file: Uploaded CSV file
        
    Returns:
        UploadResponse: Response with upload ID and initial status
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
        
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )
    
    upload_id = str(uuid.uuid4())
    file_location = os.path.join(UPLOAD_DIR, f"{upload_id}_{file.filename}")
    
    logger.info(f"Received upload: {file.filename} (ID: {upload_id})")
    
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Saved file to: {file_location}")
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}"
        )
    finally:
        file.file.close()
    
    upload_tasks[upload_id] = {
        "id": upload_id,
        "filename": file.filename,
        "status": UploadStatus.PENDING,
        "message": "Upload received. Processing will begin shortly.",
        "processed": 0,
        "skipped": 0,
        "failed": 0,
        "total_records": 0,
        "error_details": [],
        "created_at": datetime.datetime.now()
    }
    
    background_tasks.add_task(process_csv_file, file_location, upload_id)
    
    return UploadResponse(
        id=upload_id,
        filename=file.filename,
        status=UploadStatus.PENDING,
        message="Upload received. Processing will begin shortly."
    )


@router.get("/{upload_id}", response_model=UploadResponse)
async def get_upload_status(upload_id: str):
    """
    Get the status of a SWIFT code upload task.
    
    Args:
        upload_id: ID of the upload task
        
    Returns:
        UploadResponse: Status of the upload task
    """
    if upload_id not in upload_tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Upload with ID {upload_id} not found"
        )
    
    task = upload_tasks[upload_id]
    
    response_data = {
        "id": task["id"],
        "filename": task["filename"],
        "status": task["status"],
        "message": task["message"],
        "processed": task["processed"],
        "skipped": task.get("skipped", 0),
        "failed": task["failed"],
        "total_records": task["total_records"],
        "error_details": task["error_details"]
    }
    
    if "created_at" in task and task["created_at"] is not None:
        response_data["created_at"] = task["created_at"]
    
    return UploadResponse(**response_data)


@router.get("/", response_model=List[UploadResponse])
async def list_uploads(
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
    status: Optional[UploadStatus] = None
):
    """
    List all SWIFT code upload tasks with optional filtering.
    
    Args:
        limit: Maximum number of tasks to return
        skip: Number of tasks to skip
        status: Filter by upload status
        
    Returns:
        List[UploadResponse]: List of upload tasks
    """
    all_tasks = list(upload_tasks.values())
    
    if status:
        all_tasks = [task for task in all_tasks if task["status"] == status]
    
    all_tasks.sort(key=lambda x: x.get("created_at", datetime.datetime.min), reverse=True)
    
    paginated_tasks = all_tasks[skip:skip+limit]
    
    result = []
    for task in paginated_tasks:
        response_data = {
            "id": task["id"],
            "filename": task["filename"],
            "status": task["status"],
            "message": task["message"],
            "processed": task["processed"],
            "skipped": task.get("skipped", 0),
            "failed": task["failed"],
            "total_records": task["total_records"],
            "error_details": task["error_details"]
        }
        
        if "created_at" in task and task["created_at"] is not None:
            response_data["created_at"] = task["created_at"]
        
        result.append(UploadResponse(**response_data))
    
    return result


@router.get("/stats/summary", response_model=UploadStatsResponse)
async def get_upload_stats():
    """
    Get summary statistics for all uploads.
    
    Returns:
        UploadStatsResponse: Summary statistics
    """
    all_tasks = list(upload_tasks.values())
    
    total_uploads = len(all_tasks)
    successful_uploads = len([task for task in all_tasks if task["status"] == UploadStatus.COMPLETED])
    failed_uploads = len([task for task in all_tasks if task["status"] == UploadStatus.FAILED])
    processing_uploads = len([task for task in all_tasks if task["status"] in 
                             [UploadStatus.PENDING, UploadStatus.PROCESSING]])
    
    records_processed = sum(task["processed"] for task in all_tasks)
    
    most_recent_upload = None
    if all_tasks:
        valid_timestamps = [task.get("created_at") for task in all_tasks 
                          if task.get("created_at") is not None]
        most_recent_upload = max(valid_timestamps) if valid_timestamps else None
    
    return UploadStatsResponse(
        total_uploads=total_uploads,
        successful_uploads=successful_uploads,
        failed_uploads=failed_uploads,
        processing_uploads=processing_uploads,
        records_processed=records_processed,
        most_recent_upload=most_recent_upload
    )