"""Custom exceptions for the Student Record Management System.

Every exception inherits from StudentSystemError, so the interface can catch
all expected problems with one ``except`` clause while still telling them apart.
"""


class StudentSystemError(Exception):
    """Base class for every expected error in the application."""


class ValidationError(StudentSystemError):
    """Raised when a value breaks a validation rule (e.g. a mark of 120)."""


class DuplicateStudentError(StudentSystemError):
    """Raised when adding a student whose ID already exists."""


class StudentNotFoundError(StudentSystemError):
    """Raised when no student matches the requested ID."""


class DataFileError(StudentSystemError):
    """Raised when the data file cannot be read, parsed, or written."""
