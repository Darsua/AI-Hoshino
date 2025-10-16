import random
import copy

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

    def add_meeting(self, meeting: 'State.Allocation'):
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

    def get_random_neighbor(self, rooms: dict[str, Room]):
        neighbor = State()
        neighbor.meetings = [copy.copy(m) for m in self.meetings]

        if len(neighbor.meetings) < 2:
            return neighbor
        if random.random() < 0.5:
            m1, m2 = random.sample(neighbor.meetings, 2)
            m1.time_slot, m2.time_slot = m2.time_slot, m1.time_slot
            m1.room, m2.room = m2.room, m1.room
        else:
            meeting_to_change = random.choice(neighbor.meetings)
            duration = meeting_to_change.time_slot.duration()
            max_attempts = 100
            for _ in range(max_attempts):
                day = TimeSlot.Day(random.randint(0, 4))
                start_hour = random.randint(7, 18 - duration)
                end_hour = start_hour + duration
                new_time_slot = TimeSlot(day, start_hour, end_hour)
                new_room = random.choice(list(rooms.values()))
                conflict = False
                for other_meeting in neighbor.meetings:
                    if other_meeting != meeting_to_change and \
                    other_meeting.time_slot.day == day and \
                    other_meeting.time_slot.overlaps_with(new_time_slot) and \
                    other_meeting.room == new_room:
                        conflict = True
                        break

                if not conflict:
                    meeting_to_change.time_slot = new_time_slot
                    meeting_to_change.room = new_room
                    break
            
        return neighbor

    def get_N_random_neighbors(self, N: int, rooms: dict[str, Room]):
        return [self.get_random_neighbor(rooms) for _ in range(N)]