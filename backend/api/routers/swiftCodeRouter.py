from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from api.schemas.SwiftCodeResponse import SwiftCodeResponse
from api.schemas.SwiftCodeCreate import SwiftCodeCreate

from db.database import get_db
from db.models.SwiftCode import SwiftCode

router = APIRouter(
    prefix="/api/v1/swift-code",
    tags=["swift-code"],
    responses={404: {"description": "Not found"}}
)


@router.post("/", response_model=SwiftCodeResponse, status_code=status.HTTP_201_CREATED)
def create_swift_code(swift_code: SwiftCodeCreate, db: Session = Depends(get_db)):
    """
    Create a new SWIFT code.

    Args:
        swift_code: The SWIFT code data to create
        db: Database session

    Returns:
        The created SWIFT code

    Raises:
        HTTPException: If the SWIFT code already exists or if validation fails
    """

    db_swift_code = db.query(SwiftCode).filter(
        SwiftCode.swiftCode == swift_code.swiftCode).first()
    if db_swift_code:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"SWIFT code {swift_code.swiftCode} already exists"
        )

    try:
        db_swift_code = SwiftCode(
            swiftCode=swift_code.swiftCode,
            address=swift_code.address,
            countryISO2=swift_code.countryISO2,
            countryName=swift_code.countryName,
            isHeadquarter=swift_code.isHeadquarter
        )

        db.add(db_swift_code)
        db.commit()
        db.refresh(db_swift_code)
        return db_swift_code
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except SQLAlchemyError as e:
        db.rollback()
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
    db: Session = Depends(get_db)
):
    """
    Get all SWIFT codes with optional filtering.

    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return (pagination)
        country: Optional filter by country ISO code
        is_headquarter: Optional filter by headquarter status
        db: Database session

    Returns:
        List of SWIFT codes matching the criteria
    """
    query = db.query(SwiftCode)

    if country:
        query = query.filter(SwiftCode.countryISO2 == country.upper())
    if is_headquarter is not None:
        query = query.filter(SwiftCode.isHeadquarter == is_headquarter)

    return query.offset(skip).limit(limit).all()


@router.get("/{swift_code}", response_model=SwiftCodeResponse)
def get_swift_code(swift_code: str, db: Session = Depends(get_db)):
    """
    Get a specific SWIFT code by its code.

    Args:
        swift_code: The SWIFT code to retrieve
        db: Database session

    Returns:
        The requested SWIFT code

    Raises:
        HTTPException: If the SWIFT code is not found
    """
    db_swift_code = db.query(SwiftCode).filter(
        SwiftCode.swiftCode == swift_code.upper()).first()
    if not db_swift_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SWIFT code {swift_code} not found"
        )
    return db_swift_code


@router.delete("/{swift_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_swift_code(swift_code: str, db: Session = Depends(get_db)):
    """
    Delete a SWIFT code.

    Args:
        swift_code: The SWIFT code to delete
        db: Database session

    Raises:
        HTTPException: If the SWIFT code is not found
    """
    db_swift_code = db.query(SwiftCode).filter(
        SwiftCode.swiftCode == swift_code.upper()).first()
    if not db_swift_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SWIFT code {swift_code} not found"
        )

    try:
        db.delete(db_swift_code)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
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
    db: Session = Depends(get_db)
):
    """
    Get the total count of SWIFT codes with optional filtering.

    Args:
        country: Optional filter by country ISO code
        is_headquarter: Optional filter by headquarter status
        db: Database session

    Returns:
        Dict with count of SWIFT codes matching the criteria
    """
    query = db.query(SwiftCode)

    if country:
        query = query.filter(SwiftCode.countryISO2 == country.upper())
    if is_headquarter is not None:
        query = query.filter(SwiftCode.isHeadquarter == is_headquarter)

    count = query.count()
    return {"count": count}
