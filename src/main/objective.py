from src.main.state import State

class ObjectiveFunction:
    PRIORITY_WEIGHTS = {
        1: 1.75,
        2: 1.50,
        3: 1.25
    }

    def __init__(self, student_conflict=True, room_conflict=True, capacity=True):
        self.student_conflict = student_conflict
        self.room_conflict = room_conflict
        self.capacity = capacity

    def calculate(self, state) -> float:
        total_penalty = 0.0
        # if self.student_conflict:
        #     total_penalty += self._calculate_student_conflict_penalty(state)
        # if self.room_conflict:
        #     total_penalty += self._calculate_room_conflict_penalty(state)
        total_penalty += self.calculate_time_conflict_penalty(state)
        return total_penalty

    def calculate_time_conflict_penalty(self, state: State) -> float:
        penalty = 0

        # Group meetings by student
        student_meetings = {}

        for meeting in state.meetings:
            for student in meeting.course_class.students:
                if student.id not in student_meetings:
                    student_meetings[student.id] = []
                student_meetings[student.id].append(meeting)

        # Calculate conflicts for each student
        for student_id, meetings in student_meetings.items():
            # Check each pair of meetings for time conflicts
            for i in range(len(meetings)):
                for j in range(i + 1, len(meetings)):
                    meeting1 = meetings[i]
                    meeting2 = meetings[j]

                    # Check if meetings are on the same day
                    if meeting1.time_slot.day == meeting2.time_slot.day:
                        # Calculate overlap
                        start1, end1 = meeting1.time_slot.start_hour, meeting1.time_slot.end_hour
                        start2, end2 = meeting2.time_slot.start_hour, meeting2.time_slot.end_hour

                        # Find overlap hours
                        overlap_start = max(start1, start2)
                        overlap_end = min(end1, end2)

                        if overlap_start < overlap_end:
                            # Add the number of overlapping hours to penalty
                            penalty += overlap_end - overlap_start

                            # DEBUG: Print who is conflicting and which classes at what time, along with the penalty added
                            print(f"Conflict: for student {student_id} between {meeting1.course_class.code} and {meeting2.course_class.code} from {overlap_start} to {overlap_end}, adding penalty {overlap_end - overlap_start}")

        return penalty
    
    def _calculate_capacity_penalty(self, state):
        penalty = 0.0
        for meeting in state.meetings:
            student_count = meeting.course_class.studentCount
            room_capacity = meeting.room.capacity
            if student_count > room_capacity:
                # print(meeting.course_class.code, meeting.room.code, meeting.time_slot.day.name, meeting.time_slot.start_hour, meeting.time_slot.end_hour)
                # print()
                # print(student_count)
                # print()
                # print(room_capacity)
                # print()
                overflow = student_count - room_capacity 
                duration = meeting.time_slot.duration()
                # print(overflow, duration)
                penalty += overflow *duration
        return penalty
