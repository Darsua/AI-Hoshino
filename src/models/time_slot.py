from enum import Enum

class Day(Enum):
            MONDAY = 0
            TUESDAY = 1
            WEDNESDAY = 2
            THURSDAY = 3
            FRIDAY = 4
            SATURDAY = 5
            SUNDAY = 6
            
class TimeSlot:
    def __init__(self, day: Day, start_hour: int, end_hour: int):
        self.day = day
        self.start_hour = start_hour
        self.end_hour = end_hour
    
    def duration(self) -> int:
        return self.end_hour - self.start_hour
    
    def overlaps_with(self, other: 'TimeSlot') -> bool:
        if self.day != other.day:
            return False
        return not (self.end_hour <= other.start_hour or self.start_hour >= other.end_hour)
    
    def get_overlap_duration(self, other: 'TimeSlot') -> int:
        if not self.overlaps_with(other):
            return 0
        overlap_start = max(self.start_hour, other.start_hour)
        overlap_end = min(self.end_hour, other.end_hour)
        return overlap_end - overlap_start