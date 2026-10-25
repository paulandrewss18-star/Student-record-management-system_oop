"""Domain classes: Person (base class) and Student (subclass).

Attributes are stored privately and exposed through properties, so every
assignment - in the constructor, during an update, or when loading from
JSON - goes through the same validation.
"""
from exceptions import ValidationError
from validators import (
    validate_age,
    validate_attendance,
    validate_marks,
    validate_status,
    validate_student_id,
    validate_text,
)

PASS_MARK = 40

# (minimum average, label), checked from the top down.
PERFORMANCE_BANDS = (
    (85, "Excellent"),
    (70, "Good"),
    (50, "Average"),
    (0, "Needs Improvement"),
)


class Person:
    """General details shared by any person in the system."""

    def __init__(self, name, age):
        self.name = name
        self.age = age

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = validate_text(value, "Name")

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):
        self._age = validate_age(value)

    def to_dict(self):
        return {"name": self.name, "age": self.age}

    def __repr__(self):
        return f"{type(self).__name__}(name={self.name!r}, age={self.age})"


class Student(Person):
    """A student with academic details. Inherits name and age from Person."""

    REQUIRED_FIELDS = ("student_id", "name", "age", "department", "marks", "attendance")
    EDITABLE_FIELDS = ("name", "age", "department", "marks", "attendance", "status")

    def __init__(self, student_id, name, age, department, marks, attendance, status="Active"):
        super().__init__(name, age)
        self._student_id = validate_student_id(student_id)
        self.department = department
        self.marks = marks
        self.attendance = attendance
        self.status = status

    # ---- identity (read-only) -------------------------------------------
    @property
    def student_id(self):
        return self._student_id

    # ---- validated attributes ---------------------------------------------
    @property
    def department(self):
        return self._department

    @department.setter
    def department(self, value):
        self._department = validate_text(value, "Department").upper()

    @property
    def marks(self):
        # Return a tuple so callers cannot change the marks without validation.
        return tuple(self._marks)

    @marks.setter
    def marks(self, values):
        self._marks = validate_marks(values)

    @property
    def attendance(self):
        return self._attendance

    @attendance.setter
    def attendance(self, value):
        self._attendance = validate_attendance(value)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = validate_status(value)

    # ---- derived values ---------------------------------------------------
    @property
    def average(self):
        return sum(self._marks) / len(self._marks)

    @property
    def result(self):
        """PASS only if every subject mark reaches the pass mark."""
        return "PASS" if all(mark >= PASS_MARK for mark in self._marks) else "FAIL"

    @property
    def performance(self):
        for minimum, label in PERFORMANCE_BANDS:
            if self.average >= minimum:
                return label
        return PERFORMANCE_BANDS[-1][1]

    @property
    def is_active(self):
        return self.status == "Active"

    # ---- behaviour --------------------------------------------------------
    def update(self, **changes):
        """Change several fields at once; nothing changes if any value is invalid."""
        if "student_id" in changes:
            raise ValidationError("Student ID cannot be changed.")
        unknown = sorted(set(changes) - set(self.EDITABLE_FIELDS))
        if unknown:
            raise ValidationError(f"Unknown field(s): {', '.join(unknown)}.")
        # Build a throwaway copy first so every new value is checked together.
        checked = type(self).from_dict({**self.to_dict(), **changes})
        for field in changes:
            setattr(self, field, getattr(checked, field))

    # ---- conversion -------------------------------------------------------
    def to_dict(self):
        return {
            "student_id": self.student_id,
            **super().to_dict(),
            "department": self.department,
            "marks": list(self._marks),
            "attendance": self.attendance,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise ValidationError("Each record must be a JSON object.")
        missing = [field for field in cls.REQUIRED_FIELDS if field not in data]
        if missing:
            raise ValidationError(f"Missing field(s): {', '.join(missing)}.")
        details = {field: data[field] for field in cls.REQUIRED_FIELDS}
        # Records saved by the Task 2 version have no status; treat them as active.
        return cls(**details, status=data.get("status", "Active"))

    def __str__(self):
        return f"{self.student_id} | {self.name} | {self.department}"

    def __repr__(self):
        return f"Student(student_id={self.student_id!r}, name={self.name!r})"
