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
            result += f"{day.name:20} "
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
                    result += f"{cell_content:20} "
                result += "\n"

        return result

    def add_meeting(self, meeting: "State.Allocation"):
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

    def get_all_neighbors(self, rooms: dict[str, Room]):
        neighbors = []
        room_list = list(rooms.values())

        # Pre-generate all valid time slots grouped by duration for efficiency
        slots_by_duration = {}
        for duration in range(1, 11):  # Reasonable max duration
            slots_by_duration[duration] = []
            for day_val in range(5):  # Monday..Friday
                day = TimeSlot.Day(day_val)
                for start_hour in range(7, min(18, 18 - duration + 1)):
                    end_hour = start_hour + duration
                    slots_by_duration[duration].append(
                        TimeSlot(day, start_hour, end_hour)
                    )

        # 1) Move operations: try different time slots and rooms for each meeting
        for i, meeting in enumerate(self.meetings):
            duration = meeting.time_slot.duration()

            # Get pre-computed valid time slots for this duration
            valid_slots = slots_by_duration.get(duration, [])

            for new_slot in valid_slots:
                for room in room_list:
                    # Skip if identical to current placement
                    if (
                        room == meeting.room
                        and meeting.time_slot.day == new_slot.day
                        and meeting.time_slot.start_hour == new_slot.start_hour
                    ):
                        continue

                    # Create neighbor more efficiently
                    neighbor = copy.deepcopy(self)
                    neighbor.meetings[i] = State.Allocation(
                        meeting.course_class, new_slot, room
                    )
                    neighbors.append(neighbor)

        # 2) Swap operations: swap room and time slot between pairs of meetings
        n = len(self.meetings)
        for i in range(n):
            for j in range(i + 1, n):
                mi = self.meetings[i]
                mj = self.meetings[j]

                # Skip if swapping results in identical state
                if (
                    mi.time_slot.day == mj.time_slot.day
                    and mi.time_slot.start_hour == mj.time_slot.start_hour
                    and mi.time_slot.end_hour == mj.time_slot.end_hour
                    and mi.room == mj.room
                ):
                    continue

                # Create neighbor with swapped assignments
                neighbor = copy.deepcopy(self)
                neighbor.meetings[i] = State.Allocation(
                    mi.course_class, mj.time_slot, mj.room
                )
                neighbor.meetings[j] = State.Allocation(
                    mj.course_class, mi.time_slot, mi.room
                )
                neighbors.append(neighbor)

        return neighbors

    def get_random_neighbor(self, rooms: dict[str, Room]) -> "State":
        if not self.meetings:
            return None

        neighbor = State()
        # Deep copy meetings with new TimeSlot objects
        neighbor.meetings = [
            State.Allocation(
                meeting.course_class,
                TimeSlot(
                    meeting.time_slot.day,
                    meeting.time_slot.start_hour,
                    meeting.time_slot.end_hour,
                ),
                meeting.room,
            )
            for meeting in self.meetings
        ]

        # Choose operation: swap two meetings or move one
        operation = random.choice(["swap", "move"])
        n = len(neighbor.meetings)

        if operation == "swap" and n >= 2:
            # Swap time slots and rooms of two random meetings
            idx1, idx2 = random.sample(range(n), 2)
            meeting1 = neighbor.meetings[idx1]
            meeting2 = neighbor.meetings[idx2]

            # Swap time slots
            meeting1.time_slot, meeting2.time_slot = (
                meeting2.time_slot,
                meeting1.time_slot,
            )
            # Swap rooms
            meeting1.room, meeting2.room = meeting2.room, meeting1.room
        else:
            # Move: assign random new time slot and room to one meeting
            idx = random.randint(0, n - 1)
            meeting = neighbor.meetings[idx]

            # Generate new time slot with same duration
            day = TimeSlot.Day(random.randint(0, 4))
            start_hour = random.randint(7, 17)
            duration = meeting.time_slot.duration()
            end_hour = min(start_hour + duration, 18)
            meeting.time_slot = TimeSlot(day, start_hour, end_hour)

            # Assign random room
            room_list = list(rooms.values())
            meeting.room = random.choice(room_list)

        return neighbor
