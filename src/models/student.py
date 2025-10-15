class Student:
    def __init__(self, id: str, classes: list[str]):
        self.id = id
        self.classes = classes
        
    def get_priority(self, class_code: str) -> int:
        try:
            return self.classes.index(class_code) + 1
        except ValueError:
            return len(self.classes) + 1 