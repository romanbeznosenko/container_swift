from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.database import Database

from api.schemas.SwiftCodeResponse import SwiftCodeResponse
from api.schemas.SwiftCodeCreate import SwiftCodeCreate

from db.database import get_db
from db.models.SwiftCode import SwiftCode, SwiftCodeRepository

router = APIRouter(
    prefix="/api/v1/swift-code",
    tags=["swift-code"],
    responses={404: {"description": "Not found"}}
)


def get_swift_code_repository(db: Database = Depends(get_db)) -> SwiftCodeRepository:
    """Dependency to get SwiftCode repository."""
    return SwiftCodeRepository(db)


@router.post("/", response_model=SwiftCodeResponse, status_code=status.HTTP_201_CREATED)
def create_swift_code(
    swift_code: SwiftCodeCreate,
    repo: SwiftCodeRepository = Depends(get_swift_code_repository)
):
    """
    Create a new SWIFT code.

    Args:
        swift_code: The SWIFT code data to create
        repo: SwiftCode repository instance

    Returns:
        The created SWIFT code

    Raises:
        HTTPException: If the SWIFT code already exists or if validation fails
    """

    # Check if SWIFT code already exists
    existing_swift_code = repo.find_by_swift_code(swift_code.swiftCode)
    if existing_swift_code:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"SWIFT code {swift_code.swiftCode} already exists"
        )

    try:
        # Validate the swift code data
        swift_code_model = SwiftCode(**swift_code.model_dump())

        # Convert to dict for MongoDB insertion
        swift_code_dict = swift_code_model.model_dump(exclude={"id"})

        # Create the document
        created_swift_code = repo.create(swift_code_dict)

        # Convert back to SwiftCode model for response
        return SwiftCode(**created_swift_code)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"SWIFT code {swift_code.swiftCode} already exists"
        )
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.get("/", response_model=List[SwiftCodeResponse])
def get_swift_codes(
    skip: int = 0,
    limit: int = 100,
    country: Optional[str] = Query(
        None, description="Filter by country ISO code"),
    is_headquarter: Optional[bool] = Query(
        None, description="Filter by headquarter status"),
    repo: SwiftCodeRepository = Depends(get_swift_code_repository)
):
    """
    Get all SWIFT codes with optional filtering.

    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return (pagination)
        country: Optional filter by country ISO code
        is_headquarter: Optional filter by headquarter status
        repo: SwiftCode repository instance

    Returns:
        List of SWIFT codes matching the criteria
    """
    try:
        # Limit the maximum number of results to prevent performance issues
        limit = min(limit, 1000)

        swift_codes = repo.find_all(
            skip=skip,
            limit=limit,
            country=country,
            is_headquarter=is_headquarter
        )

        # Convert MongoDB documents to SwiftCode models
        return [SwiftCode(**doc) for doc in swift_codes]

    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.get("/{swift_code}", response_model=SwiftCodeResponse)
def get_swift_code(
    swift_code: str,
    repo: SwiftCodeRepository = Depends(get_swift_code_repository)
):
    """
    Get a specific SWIFT code by its code.

    Args:
        swift_code: The SWIFT code to retrieve
        repo: SwiftCode repository instance

    Returns:
        The requested SWIFT code

    Raises:
        HTTPException: If the SWIFT code is not found
    """
    try:
        swift_code_doc = repo.find_by_swift_code(swift_code)
        if not swift_code_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SWIFT code {swift_code} not found"
            )

        return SwiftCode(**swift_code_doc)

    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.delete("/{swift_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_swift_code(
    swift_code: str,
    repo: SwiftCodeRepository = Depends(get_swift_code_repository)
):
    """
    Delete a SWIFT code.

    Args:
        swift_code: The SWIFT code to delete
        repo: SwiftCode repository instance

    Raises:
        HTTPException: If the SWIFT code is not found
    """
    try:
        deleted = repo.delete_by_swift_code(swift_code)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SWIFT code {swift_code} not found"
            )

    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.get("/count", response_model=dict)
def get_swift_codes_count(
    country: Optional[str] = Query(
        None, description="Filter by country ISO code"),
    is_headquarter: Optional[bool] = Query(
        None, description="Filter by headquarter status"),
    repo: SwiftCodeRepository = Depends(get_swift_code_repository)
):
    """
    Get the total count of SWIFT codes with optional filtering.

    Args:
        country: Optional filter by country ISO code
        is_headquarter: Optional filter by headquarter status
        repo: SwiftCode repository instance

    Returns:
        Dict with count of SWIFT codes matching the criteria
    """
    try:
        count = repo.count(country=country, is_headquarter=is_headquarter)
        return {"count": count}

    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
