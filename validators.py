"""Validation rules shared by the Student model and the console interface.

Keeping the rules in one module means the model and the menu can never
disagree about what a valid age, mark, or attendance value is.
"""
import math

from exceptions import ValidationError

MIN_AGE, MAX_AGE = 1, 120
MIN_PERCENT, MAX_PERCENT = 0, 100
STATUSES = ("Active", "Inactive")


def _to_number(value, field):
    """Convert value to a finite float or raise ValidationError."""
    if isinstance(value, bool):  # bool is a subclass of int; reject it explicitly
        raise ValidationError(f"{field} must be a number.")
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field} must be a number, not '{value}'.") from None
    if not math.isfinite(number):
        raise ValidationError(f"{field} must be a real number.")
    return number


def validate_text(value, field):
    """Return the stripped text, or raise if it is blank or not a string."""
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field} cannot be empty.")
    return value.strip()


def validate_student_id(value):
    """IDs are stored in upper case and may not contain spaces."""
    student_id = validate_text(value, "Student ID")
    if any(char.isspace() for char in student_id):
        raise ValidationError("Student ID cannot contain spaces.")
    return student_id.upper()


def validate_age(value):
    if isinstance(value, bool):
        raise ValidationError("Age must be a whole number.")
    if isinstance(value, float):
        if not value.is_integer():
            raise ValidationError("Age must be a whole number.")
        value = int(value)
    try:
        age = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"Age must be a whole number, not '{value}'.") from None
    if not MIN_AGE <= age <= MAX_AGE:
        raise ValidationError(f"Age must be between {MIN_AGE} and {MAX_AGE}.")
    return age


def validate_marks(values):
    """Accept a list of numbers or a comma-separated string such as '78,85,72'."""
    if isinstance(values, str):
        values = [part for part in values.split(",") if part.strip()]
    if not isinstance(values, (list, tuple)) or not values:
        raise ValidationError("Enter at least one mark.")
    marks = []
    for position, value in enumerate(values, start=1):
        mark = _to_number(value, f"Mark {position}")
        if not MIN_PERCENT <= mark <= MAX_PERCENT:
            raise ValidationError(
                f"Mark {position} ({mark:g}) must be between {MIN_PERCENT} and {MAX_PERCENT}."
            )
        marks.append(mark)
    return marks


def validate_attendance(value):
    if isinstance(value, str):
        value = value.strip().rstrip("%").strip()
    attendance = _to_number(value, "Attendance")
    if not MIN_PERCENT <= attendance <= MAX_PERCENT:
        raise ValidationError(
            f"Attendance must be between {MIN_PERCENT} and {MAX_PERCENT} percent."
        )
    return attendance


def validate_status(value):
    """Return the canonical spelling of a status ('active' -> 'Active')."""
    text = validate_text(value, "Status")
    for status in STATUSES:
        if text.casefold() == status.casefold():
            return status
    raise ValidationError(f"Status must be one of: {', '.join(STATUSES)}.")
