"""
SwiftCode MongoDB Model Module

This module defines the MongoDB document model for SWIFT/BIC codes used in international banking.
It includes comprehensive validation for SWIFT code format, country codes, and business rules
regarding headquarter designations.

A SWIFT code (or BIC - Bank Identifier Code) uniquely identifies banks and financial institutions
globally. The format follows specific rules defined by the SWIFT organization.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any
from bson import ObjectId
import re


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic v2."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type, _handler
    ):
        from pydantic_core import core_schema
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


class SwiftCode(BaseModel):
    """
    Pydantic model representing SWIFT/BIC codes for banking institutions in MongoDB.

    SWIFT codes follow the format:
    - 4 letters: Bank code
    - 2 letters: Country code (ISO)
    - 2 letters/digits: Location code
    - Optional 3 letters/digits: Branch code (XXX for headquarters)

    The complete SWIFT code is either 8 characters (primary office) or 
    11 characters (specific branch) in length.
    """

    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    swiftCode: str = Field(
        ..., description="The SWIFT/BIC code - unique identifier, max 11 characters")
    address: str = Field(...,
                         description="Physical address of the bank/branch")
    countryISO2: str = Field(...,
                             description="Two-letter ISO country code (ISO 3166-1 alpha-2)")
    countryName: str = Field(..., description="Full name of the country")
    isHeadquarter: bool = Field(
        default=False, description="Flag indicating if this is a headquarter location")

    class Config:
        # Allow population by field name and alias
        populate_by_name = True
        # JSON encoder for ObjectId
        json_encoders = {ObjectId: str}
        # Arbitrary types allowed
        arbitrary_types_allowed = True

    @field_validator('swiftCode')
    @classmethod
    def validate_swift_code(cls, v: str) -> str:
        """
        Validates the SWIFT/BIC code format.

        Rules for valid SWIFT codes:
        - Must not be empty
        - Must be either 8 or 11 characters in length
        - Must follow the pattern: [A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?
          (4 letter bank code, 2 letter country code, 2 alphanumeric location code,
           optional 3 alphanumeric branch code)
        - All letters are automatically converted to uppercase

        Args:
            v: The SWIFT code value to validate

        Returns:
            Validated and uppercase SWIFT code

        Raises:
            ValueError: If the SWIFT code is empty, has invalid length, or doesn't match pattern
        """
        if not v:
            raise ValueError("SWIFT code cannot be empty")

        v = v.upper()

        if len(v) not in (8, 11):
            raise ValueError(
                "SWIFT code must be either 8 or 11 characters long")

        pattern = r'^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$'

        if not re.match(pattern, v):
            raise ValueError("Invalid SWIFT code format")

        return v

    @field_validator('countryISO2')
    @classmethod
    def validate_country_iso(cls, v: str) -> str:
        """
        Validates the ISO country code.

        Rules for valid country codes:
        - Must not be empty
        - Must be exactly 2 characters
        - Must contain only letters (alphabetic)
        - All letters are automatically converted to uppercase

        Args:
            v: The ISO country code to validate

        Returns:
            Validated and uppercase country code

        Raises:
            ValueError: If country code is empty, not 2 characters, or contains non-alphabetic chars
        """
        if not v:
            raise ValueError("Country code cannot be empty")

        v = v.upper()

        if len(v) != 2:
            raise ValueError("Country ISO code must be exactly 2 characters")

        if not v.isalpha():
            raise ValueError("Country ISO code must contain only letters")

        return v

    def validate_swift_code_headquarters_relationship(self):
        """
        Validates the relationship between SWIFT code and headquarters status.

        Business rules:
        - SWIFT codes ending with 'XXX' (11 chars) must be headquarters (isHeadquarter=True)
        - SWIFT codes not ending with 'XXX' cannot be headquarters (isHeadquarter=False)

        Raises:
            ValueError: If the SWIFT code and headquarters flag are inconsistent
        """
        if self.swiftCode and self.isHeadquarter is not None:
            if len(self.swiftCode) == 11 and self.swiftCode.endswith("XXX"):
                if not self.isHeadquarter:
                    raise ValueError(
                        "SWIFT codes ending with XXX must be headquarters")
            else:
                if self.isHeadquarter:
                    raise ValueError(
                        "Only SWIFT codes ending with XXX can be headquarters")

    def model_post_init(self, __context) -> None:
        """Post-initialization validation."""
        self.validate_swift_code_headquarters_relationship()

    def model_dump(self, **kwargs):
        """Override model_dump method to handle ObjectId serialization."""
        d = super().model_dump(**kwargs)
        if "_id" in d:
            d["_id"] = str(d["_id"])
        return d


class SwiftCodeInDB(SwiftCode):
    """SwiftCode model as stored in database."""
    pass


class SwiftCodeRepository:
    """Repository class for SwiftCode operations in MongoDB."""

    def __init__(self, database):
        self.database = database
        self.collection = database["swift_codes"]

    async def create_index(self):
        """Create unique index on swiftCode field."""
        await self.collection.create_index("swiftCode", unique=True)

    def create_index_sync(self):
        """Create unique index on swiftCode field (synchronous)."""
        self.collection.create_index("swiftCode", unique=True)

    def find_by_swift_code(self, swift_code: str) -> Optional[dict]:
        """Find a SWIFT code document by its code."""
        return self.collection.find_one({"swiftCode": swift_code.upper()})

    def find_all(self, skip: int = 0, limit: int = 100, country: Optional[str] = None,
                 is_headquarter: Optional[bool] = None) -> list:
        """Find all SWIFT codes with optional filtering."""
        query = {}

        if country:
            query["countryISO2"] = country.upper()
        if is_headquarter is not None:
            query["isHeadquarter"] = is_headquarter

        return list(self.collection.find(query).skip(skip).limit(limit))

    def count(self, country: Optional[str] = None, is_headquarter: Optional[bool] = None) -> int:
        """Count SWIFT codes with optional filtering."""
        query = {}

        if country:
            query["countryISO2"] = country.upper()
        if is_headquarter is not None:
            query["isHeadquarter"] = is_headquarter

        return self.collection.count_documents(query)

    def create(self, swift_code_data: dict) -> dict:
        """Create a new SWIFT code document."""
        result = self.collection.insert_one(swift_code_data)
        swift_code_data["_id"] = result.inserted_id
        return swift_code_data

    def delete_by_swift_code(self, swift_code: str) -> bool:
        """Delete a SWIFT code document by its code."""
        result = self.collection.delete_one({"swiftCode": swift_code.upper()})
        return result.deleted_count > 0

    def insert_sample_data(self):
        """Insert sample data if collection is empty."""
        if self.collection.count_documents({}) == 0:
            sample_data = [
                {
                    "swiftCode": "DEUTDEFF",
                    "address": "Taunusanlage 12, 60325 Frankfurt am Main",
                    "countryISO2": "DE",
                    "countryName": "Germany",
                    "isHeadquarter": False
                },
                {
                    "swiftCode": "DEUTDEFFXXX",
                    "address": "Taunusanlage 12, 60325 Frankfurt am Main",
                    "countryISO2": "DE",
                    "countryName": "Germany",
                    "isHeadquarter": True
                },
                {
                    "swiftCode": "CHASUS33",
                    "address": "270 Park Avenue, New York",
                    "countryISO2": "US",
                    "countryName": "United States",
                    "isHeadquarter": False
                },
                {
                    "swiftCode": "CHASJPJT",
                    "address": "Tokyo Building, 2-7-3, Marunouchi, Chiyoda-ku",
                    "countryISO2": "JP",
                    "countryName": "Japan",
                    "isHeadquarter": False
                }
            ]

            self.collection.insert_many(sample_data)
            return len(sample_data)
        return 0
