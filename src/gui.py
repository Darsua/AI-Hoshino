import tkinter as tk
from tkinter import filedialog, ttk
from .utils.parser import load_input
from .main.state import State

class SchedulerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI-Hoshino: Course Scheduler")
        self.geometry("1000x750")
        self.configure(bg="#2E2E2E")

        # --- Style ---
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.dark_mode = True

        self.setup_styles()

        self.classes = {}
        self.rooms = {}
        self.students = {}
        self.state = State()

        self.create_widgets()
        self.apply_theme()

    def setup_styles(self):
        # --- Dark Theme ---
        self.dark_theme = {
            "bg": "#2E2E2E", "fg": "#EAEAEA", "header_bg": "#3C3C3C",
            "button_bg": "#4A4A4A", "button_fg": "#FFFFFF", "border": "#555555",
            "cell_bg": "#383838", "active_button": "#5A5A5A"
        }
        # --- Light Theme ---
        self.light_theme = {
            "bg": "#F0F0F0", "fg": "#000000", "header_bg": "#DCDCDC",
            "button_bg": "#E1E1E1", "button_fg": "#000000", "border": "#BDBDBD",
            "cell_bg": "#FFFFFF", "active_button": "#CFCFCF"
        }

    def apply_theme(self):
        theme = self.dark_theme if self.dark_mode else self.light_theme
        self.configure(bg=theme["bg"])

        self.style.configure(".", background=theme["bg"], foreground=theme["fg"], bordercolor=theme["border"])
        self.style.configure("TFrame", background=theme["bg"])
        self.style.configure("TLabel", background=theme["bg"], foreground=theme["fg"], font=("Segoe UI", 11))
        self.style.configure("Header.TLabel", background=theme["header_bg"], font=("Segoe UI", 12, "bold"), padding=(10, 5))
        self.style.configure("Time.TLabel", background=theme["header_bg"], font=("Segoe UI", 11), padding=(10, 5))
        self.style.configure("Room.TLabel", background=theme["bg"], foreground=theme["fg"], font=("Segoe UI", 16, "bold"))
        self.style.configure("Cell.TLabel", background=theme["cell_bg"], font=("Segoe UI", 10), padding=(10, 5))
        self.style.configure("TButton", background=theme["button_bg"], foreground=theme["button_fg"], font=("Segoe UI", 10, "bold"), borderwidth=0)
        self.style.map("TButton", background=[("active", theme["active_button"])])
        self.canvas.configure(bg=theme["bg"])

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill="both", expand=True)

        # Top bar for theme toggle
        top_bar = ttk.Frame(main_frame)
        top_bar.pack(fill="x", pady=(0, 10))
        theme_button = ttk.Button(top_bar, text="Toggle Theme", command=self.toggle_theme, style="TButton")
        theme_button.pack(side="right", padx=5, ipady=5)

        # Notebook for pages
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True)

        # --- Page 1: File Loader ---
        self.file_page = ttk.Frame(notebook, padding="10")
        notebook.add(self.file_page, text="File Management")
        self.create_file_loader_page()

        # --- Page 2: Schedule Viewer ---
        self.schedule_page = ttk.Frame(notebook, padding="10")
        notebook.add(self.schedule_page, text="Schedule Viewer")
        self.create_schedule_viewer_page()

    def create_file_loader_page(self):
        # Control frame
        control_frame = ttk.Frame(self.file_page)
        control_frame.pack(fill="x", pady=10)

        load_file_button = ttk.Button(control_frame, text="Load File(s)", command=self.load_files, style="TButton")
        load_file_button.pack(side="left", padx=5, ipady=5)

        load_folder_button = ttk.Button(control_frame, text="Load Folder", command=self.load_folder, style="TButton")
        load_folder_button.pack(side="left", padx=5, ipady=5)

        # Listbox to show loaded files
        self.loaded_files_list = tk.Listbox(self.file_page, bg="#3C3C3C", fg="#EAEAEA", selectbackground="#5A5A5A", borderwidth=0, highlightthickness=0)
        self.loaded_files_list.pack(fill="both", expand=True, pady=10)

    def create_schedule_viewer_page(self):
        # Control frame
        control_frame = ttk.Frame(self.schedule_page)
        control_frame.pack(fill="x", pady=10)

        # Dropdown for file selection
        self.selected_file = tk.StringVar()
        self.file_dropdown = ttk.Combobox(control_frame, textvariable=self.selected_file, state="readonly", width=50)
        self.file_dropdown.pack(side="left", padx=5)

        # Generate button
        generate_button = ttk.Button(control_frame, text="Generate Schedule", command=self.generate_schedule, style="TButton")
        generate_button.pack(side="left", padx=5, ipady=5)

        # Canvas for scrolling
        self.canvas = tk.Canvas(self.schedule_page, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.apply_theme() # Apply theme to canvas

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.schedule_page, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Frame inside canvas
        self.schedule_display_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.schedule_display_frame, anchor="nw")
        self.schedule_display_frame.bind("<Configure>", self.on_frame_configure)

    def on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def load_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Select Input JSON File(s)",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        if not file_paths:
            return
        self.update_file_list(file_paths)

    def load_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder")
        if not folder_path:
            return
        import os
        file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.json')]
        self.update_file_list(file_paths)

    def update_file_list(self, new_paths):
        import os
        
        # Store a mapping from shortened name to full path
        if not hasattr(self, 'path_map'):
            self.path_map = {}

        for path in new_paths:
            short_name = os.path.join(os.path.basename(os.path.dirname(path)), os.path.basename(path))
            if short_name not in self.path_map:
                self.path_map[short_name] = path
                self.loaded_files_list.insert(tk.END, short_name)
        
        self.file_dropdown['values'] = sorted(list(self.path_map.keys()))
        if self.loaded_files_list.size() > 0 and not self.selected_file.get():
            self.selected_file.set(sorted(list(self.path_map.keys()))[0])

    def generate_schedule(self):
        short_name = self.selected_file.get()
        if not short_name:
            print("Please load and select a file first.")
            return

        file_path = self.path_map.get(short_name)
        if not file_path:
            print(f"Error: Could not find the full path for {short_name}")
            return

        try:
            self.classes, self.rooms, self.students = load_input(file_path)
            print(f"Generating schedule for {file_path}")
        except (FileNotFoundError, ValueError) as e:
            print(f"Error loading file: {e}")
            return

        self.state = State()
        self.state.random_fill(self.classes, self.rooms)
        self.display_all_schedules()

    def display_all_schedules(self):
        for widget in self.schedule_display_frame.winfo_children():
            widget.destroy()

        if not self.state:
            return

        sorted_rooms = sorted(self.rooms.values(), key=lambda r: r.code)

        for room in sorted_rooms:
            self.create_schedule_grid(room)
        
        self.on_frame_configure()

    def create_schedule_grid(self, room):
        # Frame for the room schedule
        room_frame = ttk.Frame(self.schedule_display_frame, padding="10")
        room_frame.pack(pady=20, padx=20, fill="x")

        # Room code label
        room_label = ttk.Label(room_frame, text=f"Kode ruang: {room.code}", style="Room.TLabel")
        room_label.pack(pady=(0, 10), anchor="w")

        # Grid frame
        grid_frame = ttk.Frame(room_frame)
        grid_frame.pack(fill="x", expand=True)

        # Header
        headers = ["Jam", "Senin", "Selasa", "Rabu", "Kamis", "Jumat"]
        for i, header in enumerate(headers):
            label = ttk.Label(grid_frame, text=header, style="Header.TLabel", anchor="center")
            label.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)

        # Time slots
        for i in range(7, 18):  # 7 AM to 5 PM
            label = ttk.Label(grid_frame, text=f"{i:02d}:00", style="Time.TLabel", anchor="center")
            label.grid(row=i - 6, column=0, sticky="nsew", padx=1, pady=1)

        # Schedule data
        schedule = {}  # (day, hour) -> class_code
        for meeting in self.state.meetings:
            if meeting.room.code == room.code:
                day_map = {"MONDAY": 1, "TUESDAY": 2, "WEDNESDAY": 3, "THURSDAY": 4, "FRIDAY": 5}
                day_index = day_map.get(meeting.time_slot.day.name)
                if day_index is not None:
                    for hour in range(meeting.time_slot.start_hour, meeting.time_slot.end_hour):
                        schedule[(day_index, hour)] = meeting.course_class.code

        # Fill grid
        for day in range(1, 6):  # Mon-Fri
            for hour in range(7, 18):  # 7-17
                class_code = schedule.get((day, hour), "")
                cell_label = ttk.Label(grid_frame, text=class_code, style="Cell.TLabel", anchor="center")
                cell_label.grid(row=hour - 6, column=day, sticky="nsew", padx=1, pady=1)

        # Configure grid weights
        for i in range(len(headers)):
            grid_frame.grid_columnconfigure(i, weight=1, minsize=120)
        for i in range(12):
            grid_frame.grid_rowconfigure(i, weight=1, minsize=40)


if __name__ == "__main__":
    app = SchedulerGUI()
    app.mainloop()