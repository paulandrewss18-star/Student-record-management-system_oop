"""Student Record Management System (OOP version). Run: python main.py"""
from pathlib import Path

from exceptions import DataFileError, StudentSystemError, ValidationError
from file_manager import FileManager
from report_generator import ReportGenerator
from student_manager import StudentManager
from validators import (
    STATUSES,
    validate_age,
    validate_attendance,
    validate_marks,
    validate_status,
    validate_student_id,
    validate_text,
)

DATA_FILE = Path(__file__).with_name("students.json")


class ConsoleApp:
    """Menu-driven interface. Handles input and output only; the work is
    delegated to StudentManager and ReportGenerator."""

    def __init__(self, manager, reports):
        self.manager = manager
        self.reports = reports
        self.menu = (
            ("1", "Add Student", self.add_student),
            ("2", "View Students", self.view_students),
            ("3", "Search Student", self.search_student),
            ("4", "Update Student", self.update_student),
            ("5", "Delete Student", self.delete_student),
            ("6", "Performance Report", self.performance_report),
            ("7", "Exit", None),
        )

    # ---- input helpers ----------------------------------------------------
    @staticmethod
    def ask(prompt, validate, allow_blank=False):
        """Keep asking until validate() accepts the input.
        With allow_blank=True, pressing Enter returns None (keep current value)."""
        while True:
            raw = input(prompt).strip()
            if not raw and allow_blank:
                return None
            try:
                return validate(raw)
            except ValidationError as error:
                print(f"  {error}")

    @staticmethod
    def confirm(prompt):
        return input(f"{prompt} (y/n): ").strip().lower() in ("y", "yes")

    # ---- main loop --------------------------------------------------------
    def start(self):
        print("Welcome to the Student Record Management System.")
        try:
            for warning in self.manager.load():
                print(f"Warning: {warning}")
        except DataFileError as error:
            print(f"Warning: {error}\nStarting with an empty list.")
        print(f"{len(self.manager)} student record(s) loaded.")

        while True:
            print("\nChoose an option:")
            for key, label, _ in self.menu:
                print(f"{key}. {label}")
            choice = input("Enter your choice (1-7): ").strip()
            action = next((item for item in self.menu if item[0] == choice), None)
            if action is None:
                print("Invalid option. Choose a number from 1 to 7.")
                continue
            if action[2] is None:
                print("All changes are saved. Goodbye!")
                return
            try:
                action[2]()
            except StudentSystemError as error:
                print(f"Error: {error}")

    # ---- menu actions -----------------------------------------------------
    def add_student(self):
        print("\nADD STUDENT")
        student_id = self.ask("Student ID (unique): ", validate_student_id)
        if self.manager.exists(student_id):
            print(f"Student ID {student_id} already exists.")
            return
        student = self.manager.create(
            student_id=student_id,
            name=self.ask("Student Name: ", lambda v: validate_text(v, "Name")),
            age=self.ask("Age: ", validate_age),
            department=self.ask("Department: ", lambda v: validate_text(v, "Department")),
            marks=self.ask("Marks (comma-separated, 0-100): ", validate_marks),
            attendance=self.ask("Attendance percentage (0-100): ", validate_attendance),
        )
        print(f"Student {student.student_id} added successfully.")

    def view_students(self):
        print("\nSTUDENT RECORDS")
        print(self.reports.student_table(self.manager))

    def search_student(self):
        student_id = self.ask("Enter Student ID to search: ", validate_student_id)
        print()
        print(self.reports.student_report(self.manager.get(student_id)))

    def update_student(self):
        student_id = self.ask("Enter Student ID to update: ", validate_student_id)
        student = self.manager.get(student_id)
        print(f"Updating {student}. Press Enter to keep the current value.")
        marks_now = ",".join(f"{m:g}" for m in student.marks)
        answers = {
            "name": self.ask(f"Name [{student.name}]: ",
                             lambda v: validate_text(v, "Name"), allow_blank=True),
            "age": self.ask(f"Age [{student.age}]: ", validate_age, allow_blank=True),
            "department": self.ask(f"Department [{student.department}]: ",
                                   lambda v: validate_text(v, "Department"), allow_blank=True),
            "marks": self.ask(f"Marks [{marks_now}]: ", validate_marks, allow_blank=True),
            "attendance": self.ask(f"Attendance [{student.attendance:g}]: ",
                                   validate_attendance, allow_blank=True),
            "status": self.ask(f"Status [{student.status}] ({'/'.join(STATUSES)}): ",
                               validate_status, allow_blank=True),
        }
        changes = {field: value for field, value in answers.items() if value is not None}
        if not changes:
            print("No changes made.")
            return
        self.manager.update(student_id, **changes)
        print(f"Student updated successfully ({', '.join(changes)}).")

    def delete_student(self):
        student_id = self.ask("Enter Student ID to delete: ", validate_student_id)
        student = self.manager.get(student_id)
        if self.confirm(f"Delete {student}?"):
            self.manager.delete(student_id)
            print("Student deleted successfully.")
        else:
            print("Deletion cancelled.")

    def performance_report(self):
        print()
        print(self.reports.performance_report(self.manager))


def main():
    manager = StudentManager(FileManager(DATA_FILE))
    app = ConsoleApp(manager, ReportGenerator())
    try:
        app.start()
    except (KeyboardInterrupt, EOFError):
        print("\nProgram stopped. Changes saved before this point are kept.")


if __name__ == "__main__":
    main()
