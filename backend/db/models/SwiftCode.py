"""
SwiftCode Model Module

This module defines the SQLAlchemy model for SWIFT/BIC codes used in international banking.
It includes comprehensive validation for SWIFT code format, country codes, and business rules
regarding headquarter designations.

A SWIFT code (or BIC - Bank Identifier Code) uniquely identifies banks and financial institutions
globally. The format follows specific rules defined by the SWIFT organization.
"""

from sqlalchemy import Column, String, Boolean, event
from sqlalchemy.orm import validates
from db.models.base import Base
import re
from typing import Optional


class SwiftCode(Base):
    """
    SQLAlchemy model representing SWIFT/BIC codes for banking institutions.

    SWIFT codes follow the format:
    - 4 letters: Bank code
    - 2 letters: Country code (ISO)
    - 2 letters/digits: Location code
    - Optional 3 letters/digits: Branch code (XXX for headquarters)

    The complete SWIFT code is either 8 characters (primary office) or 
    11 characters (specific branch) in length.
    """
    __tablename__ = "swift_codes"

    swiftCode = Column(String(11), primary_key=True,
                       doc="The SWIFT/BIC code - primary key, max 11 characters")
    address = Column(String(255),
                     doc="Physical address of the bank/branch")
    countryISO2 = Column(String(2),
                         doc="Two-letter ISO country code (ISO 3166-1 alpha-2)")
    countryName = Column(String(100),
                         doc="Full name of the country")
    isHeadquarter = Column(Boolean, default=False,
                           doc="Flag indicating if this is a headquarter location (typically has XXX suffix)")

    @validates('swiftCode')
    def validate_swift_code(self, key: str, swift_code: str) -> str:
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
            key: Field name being validated ('swiftCode')
            swift_code: The SWIFT code value to validate

        Returns:
            Validated and uppercase SWIFT code

        Raises:
            ValueError: If the SWIFT code is empty, has invalid length, or doesn't match pattern
        """
        if not swift_code:
            raise ValueError("SWIFT code cannot be empty")

        swift_code = swift_code.upper()

        if len(swift_code) not in (8, 11):
            raise ValueError(
                "SWIFT code must be either 8 or 11 characters long")

        pattern = r'^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$'

        if not re.match(pattern, swift_code):
            raise ValueError("Invalid SWIFT code format")

        return swift_code

    @validates('countryISO2')
    def validate_country_iso(self, key: str, country_code: str) -> str:
        """
        Validates the ISO country code.

        Rules for valid country codes:
        - Must not be empty
        - Must be exactly 2 characters
        - Must contain only letters (alphabetic)
        - All letters are automatically converted to uppercase

        Args:
            key: Field name being validated ('countryISO2')
            country_code: The ISO country code to validate

        Returns:
            Validated and uppercase country code

        Raises:
            ValueError: If country code is empty, not 2 characters, or contains non-alphabetic chars
        """
        if not country_code:
            raise ValueError("Country code cannot be empty")

        country_code = country_code.upper()

        if len(country_code) != 2:
            raise ValueError("Country ISO code must be exactly 2 characters")

        if not country_code.isalpha():
            raise ValueError("Country ISO code must contain only letters")

        return country_code

    @validates('isHeadquarter')
    def validate_is_headquarter(self, key: str, is_headquarter: Optional[bool]) -> Optional[bool]:
        """
        Validates that isHeadquarter is a boolean value.

        Args:
            key: Field name being validated ('isHeadquarter')
            is_headquarter: The boolean value to validate

        Returns:
            The validated boolean value

        Raises:
            ValueError: If the value is not None and not a boolean
        """
        if is_headquarter is not None and not isinstance(is_headquarter, bool):
            raise ValueError("isHeadquarter must be a boolean value")
        return is_headquarter

    def validate_swift_code_headquarters_relationship(self):
        """
        Validates the relationship between SWIFT code and headquarters status.

        Business rules:
        - SWIFT codes ending with 'XXX' (11 chars) must be headquarters (isHeadquarter=True)
        - SWIFT codes not ending with 'XXX' cannot be headquarters (isHeadquarter=False)

        This method is called by the before_insert and before_update event listeners
        to ensure cross-field validation after all fields are set.

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


@event.listens_for(SwiftCode, 'before_insert')
@event.listens_for(SwiftCode, 'before_update')
def validate_swift_code_relationships(mapper, connection, target):
    """
    SQLAlchemy event listener for validating relationships between fields.

    This event is triggered before both inserts and updates to ensure
    that the relationship between SWIFT code format and headquarter status
    is always consistent.

    Args:
        mapper: The SQLAlchemy mapper in use
        connection: The SQLAlchemy connection in use
        target: The SwiftCode instance being inserted or updated
    """
    target.validate_swift_code_headquarters_relationship()
