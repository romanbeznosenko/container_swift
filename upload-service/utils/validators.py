"""
Validator utilities for SWIFT code data.
"""

import re
from typing import Optional


def is_valid_swift_code(swift_code: Optional[str]) -> bool:
    """
    Validate if a string is a valid SWIFT/BIC code.

    SWIFT codes follow the format:
    - 4 letters: Bank code
    - 2 letters: Country code (ISO)
    - 2 letters/digits: Location code
    - Optional 3 letters/digits: Branch code (XXX for headquarters)

    Args:
        swift_code: The SWIFT code to validate

    Returns:
        bool: True if the SWIFT code is valid, False otherwise
    """
    if not swift_code or not isinstance(swift_code, str):
        return False

    swift_code = swift_code.strip()

    if len(swift_code) not in (8, 11):
        return False

    pattern = r'^[A-Za-z]{4}[A-Za-z]{2}[A-Za-z0-9]{2}([A-Za-z0-9]{3})?$'

    return bool(re.match(pattern, swift_code))


def is_valid_country_code(country_code: Optional[str]) -> bool:
    """
    Validate if a string is a valid ISO 3166-1 alpha-2 country code.

    Args:
        country_code: The country code to validate

    Returns:
        bool: True if the country code is valid, False otherwise
    """
    if not country_code or not isinstance(country_code, str):
        return False

    country_code = country_code.strip()

    if len(country_code) != 2:
        return False

    return country_code.isalpha()
