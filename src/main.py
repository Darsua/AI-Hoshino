import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import argparse

def main():
    arg_parser = argparse.ArgumentParser(description="AI-Hoshino: A scheduling problem solver")
    arg_parser.add_argument('input_file', type=str, nargs='?', default=None, help='Path to the input JSON file (required for CLI mode)')
    arg_parser.add_argument('--gui', action='store_true', help='Launch the graphical user interface')
    args = arg_parser.parse_args()

    if args.gui:
        from src.gui import SchedulerGUI
        app = SchedulerGUI()
        app.mainloop()
    else:
        if not args.input_file:
            print("Error: input_file is required when not using --gui mode.")
            arg_parser.print_help()
            exit(1)

        from src.utils.parser import load_input
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

        from src.main.state import State
        state = State()
        state.random_fill(classes, rooms)
        print(state)

if __name__ == "__main__":
    main()