import tkinter as tk
from tkinter import filedialog, ttk
import json
from src.utils.parser import load_input
from src.main.state import State

class SchedulerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI-Hoshino: Course Scheduler")
        self.geometry("800x600")

        self.classes = {}
        self.rooms = {}
        self.students = {}
        self.state = None

        self.create_widgets()

    def create_widgets(self):
        # Frame for controls
        control_frame = tk.Frame(self)
        control_frame.pack(pady=10, padx=10, fill="x")

        # Button to load file
        load_button = tk.Button(control_frame, text="Load Input File", command=self.load_file)
        load_button.pack(side="left", padx=5)

        # Button to generate schedule
        generate_button = tk.Button(control_frame, text="Generate Schedule", command=self.generate_schedule)
        generate_button.pack(side="left", padx=5)

        # Frame for schedule display
        schedule_frame = tk.Frame(self)
        schedule_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Treeview for schedule display
        self.schedule_tree = ttk.Treeview(schedule_frame)
        self.schedule_tree.pack(fill="both", expand=True)

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Input JSON File",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        if not file_path:
            return

        try:
            self.classes, self.rooms, self.students = load_input(file_path)
            # For now, just print a success message or update a status bar
            print("File loaded successfully!")
        except (FileNotFoundError, ValueError) as e:
            # In a real GUI, you'd show this in a message box
            print(f"Error loading file: {e}")


    def generate_schedule(self):
        if not self.classes or not self.rooms:
            print("Please load an input file first.")
            return

        self.state = State()
        self.state.random_fill(self.classes, self.rooms)
        self.display_schedule()

    def display_schedule(self):
        # Clear previous schedule
        for i in self.schedule_tree.get_children():
            self.schedule_tree.delete(i)

        if not self.state:
            return

        # Setup columns
        self.schedule_tree["columns"] = ("Class", "Time", "Room")
        self.schedule_tree.column("#0", width=0, stretch=tk.NO)
        self.schedule_tree.column("Class", anchor=tk.W, width=150)
        self.schedule_tree.column("Time", anchor=tk.CENTER, width=100)
        self.schedule_tree.column("Room", anchor=tk.W, width=100)

        # Setup headings
        self.schedule_tree.heading("#0", text="", anchor=tk.W)
        self.schedule_tree.heading("Class", text="Class", anchor=tk.W)
        self.schedule_tree.heading("Time", text="Time", anchor=tk.CENTER)
        self.schedule_tree.heading("Room", text="Room", anchor=tk.W)

        # Populate data
        for meeting in self.state.meetings:
            class_code = meeting.course_class.code
            time_slot = meeting.time_slot
            room_code = meeting.room.code
            time_str = f"{time_slot.day.name} {time_slot.start_hour}:00-{time_slot.end_hour}:00"
            self.schedule_tree.insert("", tk.END, values=(class_code, time_str, room_code))


if __name__ == "__main__":
    app = SchedulerGUI()
    app.mainloop()