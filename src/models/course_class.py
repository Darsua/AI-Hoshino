from src.models.student import Student

class CourseClass:
    def __init__(self, code: str, studentCount: int, credits: int):
        self.code = code
        self.studentCount = studentCount
        self.students = list[Student]()
        self.credits = credits

    def add_student(self, student):
        if student not in self.students:
            self.students.append(student)
