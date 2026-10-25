# Student Record Management System (OOP Version)

A menu-driven Python application for managing student records, refactored from
the Task 2 procedural version into classes with clear responsibilities.
Records are saved to `students.json` and loaded again on the next run.

## Requirements
- Python 3.8 or later
- No external libraries

## Run
```bash
python main.py
```
On Windows, `py main.py` may also work. Keep all the `.py` files in the same folder.

## Project structure

| File | Contents | Responsibility |
|---|---|---|
| `main.py` | `ConsoleApp` | Menu, prompts and messages. Contains no business rules. |
| `models.py` | `Person`, `Student` | The data and its rules: average, PASS/FAIL, performance band, status. |
| `student_manager.py` | `StudentManager` | Managing many students: add, find, update, delete, autosave. |
| `report_generator.py` | `ReportGenerator` | Building the student report, the records table and the performance report as text. |
| `file_manager.py` | `FileManager` | Reading and writing JSON safely. |
| `validators.py` | functions | Validation rules shared by the model and the menu. |
| `exceptions.py` | exception classes | Custom errors for invalid operations. |

Each class depends only on what it needs: `StudentManager` receives a
`FileManager`, and `ReportGenerator` works on any list of `Student` objects, so
either could be replaced (for example, a CSV file manager) without touching the rest.

## How the OOP topics are used
- **Classes and objects:** each student is a `Student` object; the application is
  built from `ConsoleApp`, `StudentManager`, `FileManager` and `ReportGenerator` objects.
- **Encapsulation:** attributes are private (`_name`, `_marks`, ...) and exposed
  through properties whose setters validate every value. The student ID is
  read-only, and `marks` is returned as a tuple so it cannot be changed without validation.
- **Inheritance:** `Student` extends `Person` (name and age), and all custom
  exceptions extend `StudentSystemError`.
- **Exception handling:** invalid operations raise specific exceptions
  (`ValidationError`, `DuplicateStudentError`, `StudentNotFoundError`, `DataFileError`),
  which the menu catches and reports without crashing.
- **Modules:** each responsibility lives in its own file.

## Menu
1. Add Student
2. View Students (table of all records)
3. Search Student (shows the Student Report)
4. Update Student (any field, including Active/Inactive status)
5. Delete Student (asks for confirmation)
6. Performance Report
7. Exit

## Sample output
```text
Student Report
---------------
ST001 | Abhay | CSE
Age: 20
Marks: 78, 85, 72
Average: 78.3%
Attendance: 91%
Performance: Good
Result: PASS
Status: Active
```

## Rules
- Student IDs are unique (case-insensitive), stored in upper case, and cannot contain spaces or be changed later.
- Name and department cannot be blank; departments are stored in upper case.
- Age must be a whole number from 1 to 120.
- Enter at least one mark; each mark must be from 0 to 100.
- Attendance must be from 0 to 100 (a trailing `%` is accepted).
- Status is `Active` or `Inactive`; new students are `Active`.
- A student passes if every subject mark is at least 40.
- Performance: Excellent (85+), Good (70-84.9), Average (50-69.9), Needs Improvement (below 50).
- The performance report flags students who failed a subject or have attendance below 75%.

## Error handling
- Every change is saved immediately. If a save fails, the change is undone in memory
  so the program and the file stay consistent, and the file is written through a
  temporary file so it is never left half-written.
- An update is all-or-nothing: if any new value is invalid, nothing is changed.
- A missing or empty `students.json` starts an empty list. A corrupt file, or one
  with invalid or duplicate records, is copied to `students.json.bak` before
  anything is overwritten, and the problem is reported.
- `students.json` files from the Task 2 version load correctly; missing statuses default to `Active`.
- Pressing Ctrl+C exits cleanly.
