# Variables
class CourseClass:
    def __init__(self, code: str, students: int, credits: int):
        self.code = code
        self.students = students
        self.credits = credits
        
class TimeSlot:
    class Time:
        def __init__(self, day: str, hour: int):
            self.day = day
            self.hour = hour
    
    def __init__(self, start: Time, end: Time):
        self.start = start
        self.end = end
        
class Room:
    def __init__(self, code: str, capacity: int):
        self.code = code
        self.capacity = capacity

class Student:
    def __init__(self, id: str, classes: dict[str, int]):
        self.id = id
        self.classes = classes  # Mapping of class code to priority

# State
class Allocation:
    def __init__(self, course_class: CourseClass, time_slots: list[TimeSlot], room: Room):
        self.course_class = course_class
        self.time_slots = time_slots
        self.room = room
        
class State:
    def __init__(self):
        self.allocations = list[Allocation]()