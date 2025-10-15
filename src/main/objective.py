from collections import defaultdict

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
        if state._objective_value is not None:
            return state._objective_value
        total_penalty = 0.0
        if self.student_conflict:
            total_penalty += self._calculate_student_conflict_penalty(state)
        if self.room_conflict:
            total_penalty += self._calculate_room_conflict_penalty(state)
        if self.capacity:
            total_penalty += self._calculate_capacity_penalty(state)
        state._objective_value = total_penalty
        return total_penalty