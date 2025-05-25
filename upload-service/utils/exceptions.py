"""
Custom exceptions for the upload service.
"""


class CSVParsingError(Exception):
    """Exception raised when there is an error parsing a CSV file."""

    def __init__(self, message="Error parsing CSV file"):
        self.message = message
        super().__init__(self.message)


class InvalidFileError(Exception):
    """Exception raised when an uploaded file is invalid."""

    def __init__(self, message="Invalid file"):
        self.message = message
        super().__init__(self.message)


class APIIntegrationError(Exception):
    """Exception raised when there is an error interacting with the SWIFT code API."""

    def __init__(self, message="Error interacting with SWIFT code API"):
        self.message = message
        super().__init__(self.message)


class MissingColumnError(Exception):
    """Exception raised when a required column is missing from a CSV file."""

    def __init__(self, column_name):
        self.column_name = column_name
        self.message = f"Required column '{column_name}' is missing from the CSV file"
        super().__init__(self.message)


class InvalidSwiftCodeError(Exception):
    """Exception raised when a SWIFT code is invalid."""

    def __init__(self, swift_code=None):
        if swift_code:
            self.message = f"Invalid SWIFT code: {swift_code}"
        else:
            self.message = "One or more SWIFT codes in the file are invalid"
        super().__init__(self.message)


class DuplicateSwiftCodeError(Exception):
    """Exception raised when duplicate SWIFT codes are found."""

    def __init__(self):
        self.message = "File contains duplicate SWIFT codes"
        super().__init__(self.message)
