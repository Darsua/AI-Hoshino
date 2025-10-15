from enum import Enum
import random

from src.models import TimeSlot, CourseClass,Room, Day

class Allocation:
    def __init__(self, course_class: CourseClass, time_slot: TimeSlot, room: Room):
        self.course_class = course_class
        self.time_slot = time_slot
        self.room = room


# State
class State:
    # def __init__(self):
    #     self.meetings = []


    def __init__(self):
        self.meetings = []

    # def __str__(self):
    #     result = "   "
    #     for day in TimeSlot.Time.Day:
    #         result += f"{day.name:10} "
    #     result += "\n"

    #     # Find the maximum number of classes in any time slot to determine row height
    #     max_classes_per_slot = 0
    #     for j in range(18-7):
    #         for i in range(7):
    #             max_classes_per_slot = max(max_classes_per_slot, len(self.matrix[i][j]))

    #     for j in range(18-7):
    #         # We might need multiple lines if there are multiple classes
    #         lines_needed = max(1, max(len(self.matrix[i][j]) for i in range(7)))

    #         for line_idx in range(lines_needed):
    #             if line_idx == 0:
    #                 result += f"{j+7:2} "
    #             else:
    #                 result += "   "

    #             for i in range(7):
    #                 cell_entries = self.matrix[i][j]
    #                 if line_idx < len(cell_entries):
    #                     cell_content = cell_entries[line_idx]
    #                 else:
    #                     cell_content = ""
    #                 result += f"{cell_content:10} "
    #             result += "\n"
    #     return result
    
    def add_meeting(self, meeting: Allocation):
        self.meetings.append(meeting)

    def random_fill(self, classes: dict[str, CourseClass], rooms: dict[str, Room]):
        self.meetings = []
        room_list = list(rooms.values())
        for cls in classes.values():
            hours_to_allocate = cls.credits
            while hours_to_allocate > 0:
                day = Day(random.randint(0, 6))
                start_hour = random.randint(7, 17)
                duration = random.randint(1, min(3, hours_to_allocate, 18 - start_hour))
                end_hour = start_hour + duration
                time_slot = TimeSlot(day, start_hour, end_hour)
                room = random.choice(room_list)
                meeting = Allocation(cls, time_slot, room)
                self.meetings.append(meeting)
                hours_to_allocate -= duration
