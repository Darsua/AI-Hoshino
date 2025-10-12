from enum import Enum

# Variables
class Student:
    def __init__(self, id: str, classes: list[str]):
        self.id = id
        self.classes = classes

class CourseClass:
    def __init__(self, code: str, studentCount: int, credits: int):
        self.code = code
        self.studentCount = studentCount
        self.students = list[Student]()
        self.credits = credits

class Room:
    def __init__(self, code: str, capacity: int):
        self.code = code
        self.capacity = capacity

class TimeSlot:
    class Time:
        class Day(Enum):
            MONDAY = 0
            TUESDAY = 1
            WEDNESDAY = 2
            THURSDAY = 3
            FRIDAY = 4
            SATURDAY = 5
            SUNDAY = 6

        def __init__(self, day: Day, hour: int):
            self.day = day
            self.hour = hour

    def __init__(self, start: Time, end: Time):
        self.start = start
        self.end = end

# State
class State:
    class Allocation:
        def __init__(self, course_class: CourseClass, meetings: list[tuple[TimeSlot, Room]]):
            self.course_class = course_class
            self.meetings = meetings

    def __init__(self):
        self.matrix = [[list[str]() for _ in range(18-7, 0, -1)] for _ in range(7)] # Matrix that represents how many hours are free from a given time
        self.allocations = dict[str, self.Allocation]()

    def __str__(self):
        result = "   "
        for day in TimeSlot.Time.Day:
            result += f"{day.name:10} "
        result += "\n"

        # Find the maximum number of classes in any time slot to determine row height
        max_classes_per_slot = 0
        for j in range(18-7):
            for i in range(7):
                max_classes_per_slot = max(max_classes_per_slot, len(self.matrix[i][j]))

        for j in range(18-7):
            # We might need multiple lines if there are multiple classes
            lines_needed = max(1, max(len(self.matrix[i][j]) for i in range(7)))

            for line_idx in range(lines_needed):
                if line_idx == 0:
                    result += f"{j+7:2} "
                else:
                    result += "   "

                for i in range(7):
                    cell_entries = self.matrix[i][j]
                    if line_idx < len(cell_entries):
                        cell_content = cell_entries[line_idx]
                    else:
                        cell_content = ""
                    result += f"{cell_content:10} "
                result += "\n"
        return result

    def random_fill(self, classes: dict[str, CourseClass], rooms: dict[str, Room]):
        import random
        for cls_code, cls in classes.items():
            meetings = list[tuple[TimeSlot, Room]]()
            hours_to_allocate = cls.credits
            while hours_to_allocate > 0:
                day = random.randint(0, 6)
                start_hour = random.randint(7, 17)
                duration = random.randint(1, min(3, hours_to_allocate, 18 - start_hour))
                end_hour = start_hour + duration
                time_slot = TimeSlot(TimeSlot.Time(TimeSlot.Time.Day(day), start_hour), TimeSlot.Time(TimeSlot.Time.Day(day), end_hour))
                room = random.choice(list(rooms.values()))
                meetings.append((time_slot, room))
                for hour in range(start_hour, end_hour):
                    if cls_code not in self.matrix[day][hour - 7]:
                        self.matrix[day][hour - 7].append(cls_code)
                hours_to_allocate -= duration
            self.allocations[cls_code] = self.Allocation(cls, meetings)
