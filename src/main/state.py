import random

from src.models import TimeSlot, CourseClass, Room

class State:
    class Allocation:
        def __init__(self, course_class: CourseClass, time_slot: TimeSlot, room: Room):
            self.course_class = course_class
            self.time_slot = time_slot
            self.room = room

    def __init__(self):
        self.meetings = []

    def __str__(self):
        # Create header
        result = "   "
        for day in TimeSlot.Day:
            result += f"{day.name:16} "
        result += "\n"

        # Create a grid to hold meetings for each time slot
        grid = {}
        for day in range(5):  # Monday to Friday (0-4)
            for hour in range(7, 18):  # 7 AM to 5 PM
                grid[(day, hour)] = []

        # Populate grid with meetings
        for meeting in self.meetings:
            day_idx = meeting.time_slot.day.value
            for hour in range(meeting.time_slot.start_hour, meeting.time_slot.end_hour):
                if (day_idx, hour) in grid:
                    display_text = f"{meeting.course_class.code}({meeting.room.code})"
                    grid[(day_idx, hour)].append(display_text)

        # Generate output for each hour
        for hour in range(7, 18):
            # Find max classes in this hour across all days
            max_classes = max(len(grid[(day, hour)]) for day in range(5))
            lines_needed = max(1, max_classes)

            for line_idx in range(lines_needed):
                if line_idx == 0:
                    result += f"{hour:2} "
                else:
                    result += "   "

                for day in range(5):
                    cell_entries = grid[(day, hour)]
                    if line_idx < len(cell_entries):
                        cell_content = cell_entries[line_idx]
                    else:
                        cell_content = ""
                    result += f"{cell_content:16} "
                result += "\n"

        return result

    def add_meeting(self, meeting: Allocation):
        self.meetings.append(meeting)

    def random_fill(self, classes: dict[str, CourseClass], rooms: dict[str, Room]):
        self.meetings = []
        room_list = list(rooms.values())
        for cls in classes.values():
            hours_to_allocate = cls.credits
            while hours_to_allocate > 0:
                day = TimeSlot.Day(random.randint(0, 4))
                start_hour = random.randint(7, 17)
                duration = random.randint(1, min(3, hours_to_allocate, 18 - start_hour))
                end_hour = start_hour + duration
                time_slot = TimeSlot(day, start_hour, end_hour)
                room = random.choice(room_list)
                meeting = self.Allocation(cls, time_slot, room)
                self.meetings.append(meeting)
                hours_to_allocate -= duration
