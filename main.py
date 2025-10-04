import argparse

arg_parser = argparse.ArgumentParser(description="AI-Hoshino: A scheduling problem solver")
arg_parser.add_argument('input_file', type=str, help='Path to the input JSON file')
args = arg_parser.parse_args()

from parser import load_input
classes, rooms, students = load_input(args.input_file)

# Test print
for cls in classes:
    print(f"Class Code: {cls.code}, Students: {cls.students}, Credits: {cls.credits}")# 
for room in rooms:
    print(f"Room Code: {room.code}, Capacity: {room.capacity}")
for student in students:
    print(f"Student ID: {student.id}, Classes: {student.classes}")
