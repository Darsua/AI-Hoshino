import argparse

arg_parser = argparse.ArgumentParser(description="AI-Hoshino: A scheduling problem solver")
arg_parser.add_argument('input_file', type=str, help='Path to the input JSON file')
args = arg_parser.parse_args()

from parser import load_input
try:
    classes, rooms, students = load_input(args.input_file)
except (FileNotFoundError, ValueError) as e:
    print(e)
    exit(1)

# DEBUG: Test print
for cls_code, cls in classes.items():
    print(f"Class {cls_code}: {cls.studentCount} students, {cls.credits} credits")
    i = 1
    for student in cls.students:
        print(f" {i}. {student.id}: Priority = {student.classes.index(cls_code) + 1}")
        i = i + 1
    print()
for room_code, room in rooms.items():
    print(f"Room {room_code}: Capacity {room.capacity}")
print()
for student_id, student in students.items():
    print(f"Student {student_id}: Classes {student.classes}")

from state import State
state = State()
state.random_fill(classes, rooms)
print(state)