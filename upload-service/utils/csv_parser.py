"""
CSV parser for SWIFT code data.
"""

import pandas as pd
from typing import List, Dict, Any
import os

from utils.validators import is_valid_swift_code
from utils.exceptions import (
    MissingColumnError,
    InvalidSwiftCodeError,
    DuplicateSwiftCodeError,
    CSVParsingError
)
from utils.logger import setup_logger

logger = setup_logger("csv_parser")


def parse_swift_data(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse and validate SWIFT code data from a CSV file.

    This function reads a CSV file containing SWIFT code information,
    validates its structure and content, and transforms it into a standardized format.
    It applies business rules such as determining headquarter status based on the
    SWIFT code ending with 'XXX' and standardizing country codes to uppercase.

    Args:
        file_path (str): Path to the CSV file containing SWIFT code data.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each representing a SWIFT code entry
        with standardized field names and formatted values.

    Raises:
        CSVParsingError: If there is an error parsing the CSV file.
        MissingColumnError: If any required columns are missing from the CSV file.
        InvalidSwiftCodeError: If any SWIFT codes in the file are not valid.
        DuplicateSwiftCodeError: If the file contains duplicate SWIFT codes.
    """
    logger.info(f"Parsing SWIFT code data from: {file_path}")

    if not os.path.isfile(file_path):
        logger.error(f"File not found: {file_path}")
        raise CSVParsingError("File not found at the specified path")

    if not file_path.lower().endswith('.csv'):
        logger.error(f"Invalid file extension: {file_path}")
        raise CSVParsingError("File must be a CSV file")

    try:
        df = pd.read_csv(file_path)
        logger.info(f"Successfully read CSV with {len(df)} rows")
    except pd.errors.ParserError as e:
        logger.error(f"Error parsing CSV: {str(e)}")
        raise CSVParsingError(f"Error parsing CSV: {str(e)}")
    except pd.errors.EmptyDataError as e:
        logger.error("CSV file is empty")
        raise CSVParsingError("CSV file is empty")
    except Exception as e:
        logger.error(f"Unexpected error reading CSV: {str(e)}")
        raise CSVParsingError(f"Unexpected error reading CSV: {str(e)}")

    logger.info(f"CSV columns: {df.columns.tolist()}")
    needed_columns = [
        'SWIFT CODE',
        'COUNTRY ISO2 CODE',
        'COUNTRY NAME',
        'NAME',
        'ADDRESS',
    ]

    for column_name in needed_columns:
        if column_name not in df.columns:
            logger.error(f"Missing required column: {column_name}")
            raise MissingColumnError(column_name)

    logger.info("Validating SWIFT codes...")
    invalid_swift_codes = df[~df['SWIFT CODE'].apply(is_valid_swift_code)]
    if not invalid_swift_codes.empty:
        logger.error(f"Found {len(invalid_swift_codes)} invalid SWIFT codes")
        logger.error(
            f"First few invalid codes: {invalid_swift_codes['SWIFT CODE'].head().tolist()}")
        raise InvalidSwiftCodeError()

    logger.info("Checking for duplicate SWIFT codes...")
    duplicate_swift_code_exists = df['SWIFT CODE'].duplicated().any()
    if duplicate_swift_code_exists:
        duplicate_codes = df[df['SWIFT CODE'].duplicated(
            keep=False)]['SWIFT CODE'].unique().tolist()
        logger.error(f"Found duplicate SWIFT codes: {duplicate_codes[:5]}")
        raise DuplicateSwiftCodeError()

    logger.info("Cleaning and standardizing data...")
    df.columns = df.columns.str.strip()

    df = df.fillna('')

    df['COUNTRY NAME'] = df['COUNTRY NAME'].astype(str).str.upper().str.strip()
    df['COUNTRY ISO2 CODE'] = df['COUNTRY ISO2 CODE'].astype(
        str).str.upper().str.strip()
    df['ADDRESS'] = df['ADDRESS'].fillna(
        '').astype(str).str.upper().str.strip()
    df['NAME'] = df['NAME'].fillna('').astype(str).str.upper().str.strip()

    df['is_headquarter'] = (df['SWIFT CODE'].fillna('').astype(str).str.len() == 11) & \
        (df['SWIFT CODE'].fillna('').astype(str).str.endswith('XXX'))

    df = df.rename(columns={
        'SWIFT CODE': 'swift_code',
        'ADDRESS': 'address',
        'NAME': 'bank_name',
        'COUNTRY ISO2 CODE': 'country_ISO2',
        'COUNTRY NAME': 'country_name'
    })

    result_df = df[['swift_code', 'address', 'bank_name',
                    'country_ISO2', 'country_name', 'is_headquarter']]

    result = result_df.to_dict(orient="records")

    logger.info(f"Successfully parsed {len(result)} SWIFT codes")
    return result
