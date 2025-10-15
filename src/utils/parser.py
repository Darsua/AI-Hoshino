import json
from src.main.state import CourseClass, Room, Student

class Parser:
    def __init__(self, json_file_path: str):
        self.json_file_path = json_file_path
        self.data = None
        self.course_classes = {}
        self.rooms = {}
        self.students = {}

    def load_json(self):
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as file:
                self.data = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file not found: {self.json_file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")

    def parse_course_classes(self) -> dict[str, CourseClass]:
        if not self.data or 'kelas_mata_kuliah' not in self.data:
            return {}

        course_classes = {}
        for item in self.data['kelas_mata_kuliah']:
            course_class = CourseClass(
                code=item['kode'],
                studentCount=item['jumlah_mahasiswa'],
                credits=item['sks']
            )
            course_classes[course_class.code] = course_class

        return course_classes

    def parse_rooms(self) -> dict[str, Room]:
        if not self.data or 'ruangan' not in self.data:
            return {}

        rooms = {}
        for item in self.data['ruangan']:
            room = Room(
                code=item['kode'],
                capacity=item['kuota']
            )
            rooms[room.code] = room

        return rooms

    def parse_students(self) -> dict[str, Student]:
        if not self.data or 'mahasiswa' not in self.data:
            return {}

        students = {}
        for item in self.data['mahasiswa']:
            # Sort classes by priority before extracting class codes
            class_priority_pairs = list(zip(item['daftar_mk'], item['prioritas']))
            sorted_pairs = sorted(class_priority_pairs, key=lambda x: x[1])
            classes = [pair[0] for pair in sorted_pairs]

            student = Student(
                id=item['nim'],
                classes=classes
            )
            students[student.id] = student

            # Add the student to the corresponding course classes
            for cls in classes:
                if cls in self.course_classes:
                    self.course_classes[cls].students.append(student)

        return students

    def verify_data(self) -> bool:
        for cls in self.course_classes.values():
            if cls.studentCount != len(cls.students):
                print(f"Error: Class {cls.code} has {len(cls.students)} students, expected {cls.studentCount}.")
                return False
        for room in self.rooms.values():
            if room.capacity <= 0:
                print(f"Error: Room {room.code} has non-positive capacity {room.capacity}.")
                return False
        for student in self.students.values():
            if not student.classes:
                print(f"Error: Student {student.id} has no classes assigned.")
                return False
        return True

    def parse_all(self):
        if not self.data:
            self.load_json()

        self.course_classes = self.parse_course_classes()
        self.rooms = self.parse_rooms()
        self.students = self.parse_students()

        if self.verify_data() is False:
            raise ValueError("Data verification failed. Please check the input JSON file for errors.")

def load_input(path: str) -> tuple[dict[str, CourseClass], dict[str, Room], dict[str, Student]]:
    parser = Parser(path)
    try:
        parser.parse_all()
    except (FileNotFoundError, ValueError) as e:
        raise(e)
    return parser.course_classes, parser.rooms, parser.students
