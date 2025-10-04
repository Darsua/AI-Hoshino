import json
from state import CourseClass, Room, Student

class Parser:
    def __init__(self, json_file_path: str):
        self.json_file_path = json_file_path
        self.data = None

    def load_json(self):
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as file:
                self.data = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file not found: {self.json_file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")

    def parse_course_classes(self) -> list[CourseClass]:
        if not self.data or 'kelas_mata_kuliah' not in self.data:
            return []

        course_classes = []
        for item in self.data['kelas_mata_kuliah']:
            course_class = CourseClass(
                code=item['kode'],
                students=item['jumlah_mahasiswa'],
                credits=item['sks']
            )
            course_classes.append(course_class)

        return course_classes

    def parse_rooms(self) -> list[Room]:
        if not self.data or 'ruangan' not in self.data:
            return []

        rooms = []
        for item in self.data['ruangan']:
            room = Room(
                code=item['kode'],
                capacity=item['kuota']
            )
            rooms.append(room)

        return rooms

    def parse_students(self) -> list[Student]:
        if not self.data or 'mahasiswa' not in self.data:
            return []

        students = []
        for item in self.data['mahasiswa']:
            # Create classes dictionary mapping class code to priority
            classes_dict = {}
            for i, class_code in enumerate(item['daftar_mk']):
                priority = item['prioritas'][i]
                classes_dict[class_code] = priority

            student = Student(
                id=item['nim'],
                classes=classes_dict
            )
            students.append(student)

        return students

    def parse_all(self) -> tuple[list[CourseClass], list[Room], list[Student]]:
        if not self.data:
            self.load_json()

        course_classes = self.parse_course_classes()
        rooms = self.parse_rooms()
        students = self.parse_students()

        return course_classes, rooms, students

def load_input(path: str) -> tuple[list[CourseClass], list[Room], list[Student]]:
    parser = Parser(path)
    return parser.parse_all()
