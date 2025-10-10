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
        class Day:
            MONDAY = "Monday"
            TUESDAY = "Tuesday"
            WEDNESDAY = "Wednesday"
            THURSDAY = "Thursday"
            FRIDAY = "Friday"
            SATURDAY = "Saturday"
            SUNDAY = "Sunday"
        
        def __init__(self, day: Day, hour: int):
            self.day = day
            self.hour = hour
    
    def __init__(self, start: Time, end: Time):
        self.start = start
        self.end = end

# State
class Allocation:
    def __init__(self, course_class: CourseClass, meetings: list[tuple[TimeSlot, Room]]):
        self.course_class = course_class
        self.meetings = meetings
        
class State:
    def __init__(self):
        self.allocations = list[Allocation]()