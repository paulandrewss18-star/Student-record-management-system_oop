"""ReportGenerator: turns student data into readable text reports.
 
It only formats text and never prints or saves, so the same reports could be
shown in the console, written to a file, or tested directly.
"""
 
LOW_ATTENDANCE = 75
 
 
def _pct(value):
    return f"{value:.1f}%"
 
 
class ReportGenerator:
    def __init__(self, low_attendance=LOW_ATTENDANCE):
        self.low_attendance = low_attendance
 
    @staticmethod
    def _title(text):
        return [text, "-" * (len(text) + 1)]
 
    def student_report(self, student):
        lines = self._title("Student Report")
        lines += [
            str(student),
            f"Average: {_pct(student.average)}",
            f"Attendance: {student.attendance:g}%",
            f"Performance: {student.performance}",
        ]
        return "\n".join(lines)
 
    def student_table(self, students):
        students = list(students)
        if not students:
            return "No student records found."
        id_w = max(len("ID"), *(len(s.student_id) for s in students))
        name_w = max(len("Name"), *(len(s.name) for s in students))
        dept_w = max(len("Dept"), *(len(s.department) for s in students))
        header = (f"{'ID':<{id_w}}  {'Name':<{name_w}}  {'Dept':<{dept_w}}  "
                  f"{'Average':>7}  {'Attend.':>7}  {'Result':<6}  Status")
        lines = [header, "-" * len(header)]
        for s in students:
            lines.append(
                f"{s.student_id:<{id_w}}  {s.name:<{name_w}}  {s.department:<{dept_w}}  "
                f"{_pct(s.average):>7}  {s.attendance:>6g}%  {s.result:<6}  {s.status}"
            )
        return "\n".join(lines)
 
    def performance_report(self, students):
        students = sorted(students, key=lambda s: (-s.average, s.name.casefold()))
        if not students:
            return "No student records available."
 
        # One Student Report per student, highest average first.
        lines = []
        for s in students:
            lines += [self.student_report(s), ""]
 
        lines += self._title("Class Summary")
        averages = [s.average for s in students]
        best = max(averages)
        toppers = [s.name for s in students if s.average == best]
        passed = sum(s.result == "PASS" for s in students)
        active = sum(s.is_active for s in students)
        lines += [
            f"Total Students: {len(students)} (Active: {active})",
            f"Class Average: {_pct(sum(averages) / len(averages))}",
            f"Passed: {passed} of {len(students)}",
            f"Top Performer: {', '.join(toppers)} ({_pct(best)})",
        ]
 
        attention = []
        for s in students:
            reasons = []
            if s.result == "FAIL":
                reasons.append("failed a subject")
            if s.attendance < self.low_attendance:
                reasons.append(f"attendance {s.attendance:g}%")
            if reasons:
                attention.append(f"  {s.student_id} {s.name}: " + "; ".join(reasons))
        if attention:
            lines.append(f"Needs Attention (fail or attendance below {self.low_attendance}%):")
            lines += attention
        return "\n".join(lines)