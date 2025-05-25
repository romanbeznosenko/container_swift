from pydantic import BaseModel, Field, field_validator, model_validator
import re


class SwiftCodeBase(BaseModel):
    """Base Pydantic model for SwiftCode with common fields."""
    swiftCode: str = Field(...,
                           description="The SWIFT/BIC code - primary key, max 11 characters")
    address: str = Field(...,
                         description="Physical address of the bank/branch")
    countryISO2: str = Field(...,
                             description="Two-letter ISO country code (ISO 3166-1 alpha-2)")
    countryName: str = Field(..., description="Full name of the country")
    isHeadquarter: bool = Field(
        False, description="Flag indicating if this is a headquarter location")

    @field_validator('swiftCode')
    @classmethod
    def validate_swift_code(cls, v: str) -> str:
        """Validate SWIFT code format."""
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
        """Validate country ISO format."""
        if not v:
            raise ValueError("Country code cannot be empty")

        v = v.upper()

        if len(v) != 2:
            raise ValueError("Country ISO code must be exactly 2 characters")

        if not v.isalpha():
            raise ValueError("Country ISO code must contain only letters")

        return v

    @model_validator(mode='after')
    def validate_headquarter_relationship(self) -> 'SwiftCodeBase':
        """Validate headquarter relationship with SWIFT code."""
        swift_code = self.swiftCode
        is_headquarter = self.isHeadquarter

        if len(swift_code) == 11 and swift_code.endswith("XXX"):
            if not is_headquarter:
                raise ValueError(
                    "SWIFT codes ending with XXX must be headquarters")
        else:
            if is_headquarter:
                raise ValueError(
                    "Only SWIFT codes ending with XXX can be headquarters")

        return self

    class Config:
        from_attributes = True
