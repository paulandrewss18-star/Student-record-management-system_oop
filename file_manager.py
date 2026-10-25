"""FileManager: reads and writes student records as JSON."""
import json
import os
import shutil
from pathlib import Path

from exceptions import DataFileError, ValidationError
from models import Student


class FileManager:
    """Handles persistence only; it knows nothing about menus or reports."""

    def __init__(self, path):
        self._path = Path(path)

    @property
    def path(self):
        return self._path

    def load(self):
        """Return (students, warnings).

        A missing or empty file gives an empty list. Invalid records are
        skipped with a warning. A corrupt file raises DataFileError. Whenever
        data would be lost on the next save, a .bak copy is kept first.
        """
        if not self._path.exists():
            return [], []
        try:
            text = self._path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            raise DataFileError(f"Could not read {self._path.name}: {error}") from error
        if not text.strip():
            return [], []

        try:
            data = json.loads(text)
        except json.JSONDecodeError as error:
            raise DataFileError(
                f"{self._path.name} is not valid JSON (line {error.lineno}). "
                + self._backup_note()
            ) from error
        if not isinstance(data, list):
            raise DataFileError(
                f"{self._path.name} must contain a list of student records. "
                + self._backup_note()
            )

        students, warnings, seen_ids = [], [], set()
        for number, record in enumerate(data, start=1):
            try:
                student = Student.from_dict(record)
            except ValidationError as error:
                warnings.append(f"Record {number} skipped: {error}")
                continue
            if student.student_id.casefold() in seen_ids:
                warnings.append(f"Record {number} skipped: duplicate ID {student.student_id}.")
                continue
            seen_ids.add(student.student_id.casefold())
            students.append(student)
        if warnings:
            warnings.append(self._backup_note())
        return students, warnings

    def save(self, students):
        """Write all students. Uses a temporary file so a failed save never
        leaves a half-written data file behind."""
        data = [student.to_dict() for student in students]
        temp_path = self._path.with_name(self._path.name + ".tmp")
        try:
            with temp_path.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            os.replace(temp_path, self._path)
        except OSError as error:
            try:
                temp_path.unlink()
            except OSError:
                pass
            raise DataFileError(f"Could not save records: {error}") from error

    def _backup_note(self):
        backup = self._path.with_name(self._path.name + ".bak")
        try:
            shutil.copy2(self._path, backup)
        except OSError:
            return "A backup copy could not be made."
        return f"The original file was copied to {backup.name}."
