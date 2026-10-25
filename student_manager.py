"""StudentManager: manages the collection of students."""
from exceptions import (
    DataFileError,
    DuplicateStudentError,
    StudentNotFoundError,
    ValidationError,
)
from models import Student


class StudentManager:
    """Adds, finds, updates, and deletes students, and saves after each change.

    If saving fails, the in-memory change is rolled back so the program and
    the data file never disagree.
    """

    def __init__(self, file_manager):
        self._file_manager = file_manager
        self._students = {}  # case-insensitive ID -> Student (keeps insertion order)

    @staticmethod
    def _key(student_id):
        return str(student_id).strip().casefold()

    # ---- persistence ------------------------------------------------------
    def load(self):
        """Load students from the file and return a list of warnings."""
        students, warnings = self._file_manager.load()
        self._students.clear()
        for student in students:
            key = self._key(student.student_id)
            if key in self._students:
                warnings.append(f"Duplicate ID {student.student_id} skipped.")
                continue
            self._students[key] = student
        return warnings

    def save(self):
        self._file_manager.save(self._students.values())

    # ---- queries ----------------------------------------------------------
    def exists(self, student_id):
        return self._key(student_id) in self._students

    def get(self, student_id):
        try:
            return self._students[self._key(student_id)]
        except KeyError:
            raise StudentNotFoundError(f"No student found with ID '{student_id}'.") from None

    def all_students(self):
        return list(self._students.values())

    def __len__(self):
        return len(self._students)

    def __iter__(self):
        return iter(self.all_students())

    # ---- changes ----------------------------------------------------------
    def add(self, student):
        if not isinstance(student, Student):
            raise ValidationError("Only Student objects can be added.")
        key = self._key(student.student_id)
        if key in self._students:
            raise DuplicateStudentError(f"Student ID {student.student_id} already exists.")
        self._students[key] = student
        try:
            self.save()
        except DataFileError:
            del self._students[key]
            raise
        return student

    def create(self, **details):
        """Build a Student from keyword arguments and add it."""
        return self.add(Student(**details))

    def update(self, student_id, **changes):
        student = self.get(student_id)
        if not changes:
            return student
        previous = student.to_dict()
        student.update(**changes)  # raises before changing anything if invalid
        try:
            self.save()
        except DataFileError:
            student.update(**{field: previous[field] for field in changes})
            raise
        return student

    def delete(self, student_id):
        student = self.get(student_id)
        snapshot = dict(self._students)
        del self._students[self._key(student_id)]
        try:
            self.save()
        except DataFileError:
            self._students = snapshot
            raise
        return student
