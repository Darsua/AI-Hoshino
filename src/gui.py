import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext
from tkinter import messagebox
from PIL import Image, ImageTk
import io
from .utils.parser import load_input
from .main.state import State
from .main.objective import ObjectiveFunction
from .algorithms.genetic import run_genetic_algorithm
from .algorithms.simulated_annealing import SimulatedAnnealing
from .algorithms.hill_climb import HillClimbing

import matplotlib
import matplotlib.pyplot as plt
import threading
import time

# Help content for AI-Hoshino Course Scheduler GUI
HELP_TEXT = """
╔═══════════════════════════════════════════════════════════════════════╗
║                    AI-HOSHINO COURSE SCHEDULER                        ║
║                         Help & Documentation                          ║
╚═══════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 GETTING STARTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Navigate to the 'Scheduler' tab
2. Load a JSON input file containing course, room, and student data
3. Select an optimization algorithm from the available options
4. Configure algorithm parameters based on your requirements
5. Click 'Run' to start the optimization process
6. View results in the output panel and visualizations in the plots section
7. Switch to 'Schedule Viewer' tab to see the optimized schedule layout


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 OPTIMIZATION ALGORITHMS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────────────────────────┐
│ HILL CLIMBING                                                        │
└─────────────────────────────────────────────────────────────────────┘
  Description:
    A local search algorithm that iteratively improves the solution by
    moving to better neighboring states. Fast execution but may converge
    to local optima.

  Variants:
    • Stochastic: Randomly selects improving neighbors
    • Steepest Ascent: Always chooses the best neighbor
    • Sideways Move: Allows plateau traversal to escape flat regions
    • Random Restart: Multiple runs with random initial states

  Best for:
    ✓ Quick solutions needed
    ✓ Smaller problem instances
    ✓ When good-enough solutions are acceptable


┌─────────────────────────────────────────────────────────────────────┐
│ SIMULATED ANNEALING                                                  │
└─────────────────────────────────────────────────────────────────────┘
  Description:
    A probabilistic optimization technique inspired by metallurgical
    annealing. Uses a temperature parameter to control the acceptance
    of worse solutions, allowing escape from local optima.

  Key Features:
    • Temperature-based probabilistic acceptance
    • Gradual cooling schedule reduces randomness over time
    • Can escape local optima early in the search
    • Converges to stable solution as temperature decreases

  Best for:
    ✓ Medium to large problem sizes
    ✓ Complex constraint landscapes
    ✓ When exploring diverse solution space is important


┌─────────────────────────────────────────────────────────────────────┐
│ GENETIC ALGORITHM                                                    │
└─────────────────────────────────────────────────────────────────────┘
  Description:
    An evolutionary algorithm that maintains a population of solutions
    and applies genetic operators (selection, crossover, mutation) to
    evolve better solutions over generations.

  Key Features:
    • Population-based approach explores multiple solutions
    • Crossover combines features from parent solutions
    • Mutation introduces diversity and prevents premature convergence
    • Tournament selection favors better individuals

  Best for:
    ✓ Complex optimization problems
    ✓ Large solution spaces requiring exploration
    ✓ When solution diversity is valuable


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ALGORITHM PARAMETERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────────────────────────┐
│ Hill Climbing Parameters                                             │
└─────────────────────────────────────────────────────────────────────┘
  Variant              Select the Hill Climbing variant to use
  Max Iterations       Maximum number of improvement iterations
  Max Sideways Moves   Plateau steps allowed (Sideways Move variant)
  Max Restarts         Number of random restarts (Random Restart variant)

┌─────────────────────────────────────────────────────────────────────┐
│ Simulated Annealing Parameters                                       │
└─────────────────────────────────────────────────────────────────────┘
  Initial Temperature  Starting temperature (higher = more exploration)
                       Recommended range: 100-1000
  Cooling Rate         Temperature decay factor per iteration
                       Recommended range: 0.90-0.99
  Max Iterations       Maximum number of iterations before termination

┌─────────────────────────────────────────────────────────────────────┐
│ Genetic Algorithm Parameters                                         │
└─────────────────────────────────────────────────────────────────────┘
  Population Size      Number of individuals per generation
                       Recommended range: 20-100
  Generations          Number of evolutionary generations
                       Recommended range: 50-500


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 UNDERSTANDING THE OUTPUT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Results Panel:
  • Initial Penalty: Quality score of the starting random schedule
  • Best Penalty: Lowest penalty score achieved (lower is better)
  • Improvement: Reduction in penalty and percentage improvement
  • Iterations: Number of optimization steps performed
  • Duration: Total execution time in seconds

Visualization Plots:
  • Objective Function: Shows penalty progression over iterations
  • Algorithm-specific metrics: Temperature, acceptance probability, etc.
  • Summary statistics: Key performance indicators

Schedule Viewer:
  • Visual representation of the optimized course schedule
  • Organized by rooms and time slots
  • Color-coded for easy identification of conflicts


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 TIPS & BEST PRACTICES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Start with default parameters for your first run
• Increase max iterations for larger datasets or better results
• Enable plot visualization to understand algorithm behavior
• Compare different algorithms on the same dataset for best results
• Use the Cancel button to stop long-running optimizations
• For Hill Climbing: Try Random Restart if stuck in local optima
• For Simulated Annealing: Higher initial temp = more exploration
• For Genetic Algorithm: Larger population = better diversity


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ADDITIONAL RESOURCES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GitHub Repository:
  https://github.com/Darsua/AI-Hoshino

For bug reports, feature requests, documentation, and source code,
please visit our GitHub repository.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Version 1.0 | © 2025 AI-Hoshino Project
"""


class SchedulerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI-Hoshino: Course Scheduler")
        self.geometry("1400x900")
        self.configure(bg="#0A0A0A")

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.dark_mode = False

        self.setup_styles()

        # Data
        self.classes = {}
        self.rooms = {}
        self.students = {}
        self.state = None
        self.current_file_path = None

        # Algorithm state
        self.is_running = False
        self.cancel_requested = False
        self.algorithm_results = None
        self.plot_images = []  # Store PhotoImage references to prevent garbage collection

        # Store HC parameter widgets for dynamic enabling/disabling
        self.hc_param_widgets = {
            "max_sideways_label": None,
            "max_sideways_entry": None,
            "max_restarts_label": None,
            "max_restarts_entry": None,
        }

        # Algorithm parameters
        self.algorithm_params = {
            "genetic": {
                "population_size": tk.IntVar(value=50),
                "generations": tk.IntVar(value=100),
            },
            "simulated_annealing": {
                "initial_temp": tk.DoubleVar(value=500.0),
                "cooling_rate": tk.DoubleVar(value=0.97),
                "max_iterations": tk.IntVar(value=5000),
            },
            "hill_climbing": {
                "variant": tk.StringVar(value="steepest_ascent"),
                "max_iterations": tk.IntVar(value=1000),
                "max_sideways_moves": tk.IntVar(value=100),
                "max_restarts": tk.IntVar(value=10),
                "restart_variant": tk.StringVar(value="steepest_ascent"),
            },
        }

        self.selected_algorithm = tk.StringVar(value="hill_climbing")
        self.show_plots = tk.BooleanVar(value=True)

        self.create_widgets()
        self.apply_theme()

    def setup_styles(self):
        self.dark_theme = {
            "bg": "#0A0A0A",
            "fg": "#EAEAEA",
            "header_bg": "#0F0F0F",
            "button_bg": "#1A1A1A",
            "button_fg": "#FFFFFF",
            "border": "#2A2A2A",
            "cell_bg": "#121212",
            "active_button": "#2A2A2A",
            "primary_button": "#6B46C1",
            "primary_hover": "#553C9A",
            "secondary_button": "#4C1D95",
            "secondary_hover": "#5B21B6",
            "disabled_bg": "#1A1A1A",
            "disabled_fg": "#888888",
            "success_bg": "#10B981",
            "text_bg": "#000000",
            "canvas_bg": "#0A0A0A",
            "plot_bg": "#0F0F0F",
            "frame_bg": "#0A0A0A",
            "labelframe_bg": "#0F0F0F",
            "entry_bg": "#1A1A1A",
            "entry_fg": "#EAEAEA",
        }
        self.light_theme = {
            "bg": "#F0F0F0",
            "fg": "#000000",
            "header_bg": "#DCDCDC",
            "button_bg": "#E1E1E1",
            "button_fg": "#000000",
            "border": "#BDBDBD",
            "cell_bg": "#FFFFFF",
            "active_button": "#CFCFCF",
            "primary_button": "#3B82F6",
            "primary_hover": "#2563EB",
            "disabled_bg": "#CCCCCC",
            "disabled_fg": "#666666",
            "success_bg": "#10B981",
            "text_bg": "#FFFFFF",
            "canvas_bg": "#F5F5F5",
            "plot_bg": "#FFFFFF",
            "frame_bg": "#F0F0F0",
            "labelframe_bg": "#FFFFFF",
            "entry_bg": "#FFFFFF",
            "entry_fg": "#000000",
        }

    def apply_theme(self):
        theme = self.dark_theme if self.dark_mode else self.light_theme
        self.configure(bg=theme["bg"])

        self.style.configure(
            ".",
            background=theme["bg"],
            foreground=theme["fg"],
            bordercolor=theme["border"],
            fieldbackground=theme["entry_bg"],
        )
        self.style.configure("TFrame", background=theme["bg"])
        self.style.configure(
            "TLabel",
            background=theme["bg"],
            foreground=theme["fg"],
            font=("Segoe UI", 11),
        )
        self.style.configure(
            "TLabelframe", background=theme["bg"], foreground=theme["fg"]
        )
        self.style.configure(
            "TLabelframe.Label",
            background=theme["bg"],
            foreground=theme["fg"],
            font=("Segoe UI", 11, "bold"),
        )
        self.style.configure(
            "Header.TLabel",
            background=theme["header_bg"],
            foreground=theme["fg"],
            font=("Segoe UI", 12, "bold"),
            padding=(10, 5),
        )
        self.style.configure(
            "Time.TLabel",
            background=theme["header_bg"],
            foreground=theme["fg"],
            font=("Segoe UI", 11),
            padding=(10, 5),
        )
        self.style.configure(
            "Room.TLabel",
            background=theme["bg"],
            foreground=theme["fg"],
            font=("Segoe UI", 16, "bold"),
        )
        self.style.configure(
            "Cell.TLabel",
            background=theme["cell_bg"],
            foreground=theme["fg"],
            font=("Segoe UI", 10),
            padding=(10, 5),
        )

        # Button styles
        self.style.configure(
            "TButton",
            background=theme["button_bg"],
            foreground=theme["button_fg"],
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
        )
        self.style.map(
            "TButton",
            background=[
                ("active", theme["active_button"]),
                ("disabled", theme["disabled_bg"]),
            ],
            foreground=[("disabled", theme["disabled_fg"])],
        )
        self.style.configure(
            "Primary.TButton", background=theme["primary_button"], foreground="#FFFFFF"
        )
        self.style.map(
            "Primary.TButton",
            background=[
                ("active", theme["primary_hover"]),
                ("disabled", theme["disabled_bg"]),
            ],
            foreground=[("disabled", theme["disabled_fg"])],
        )
        if "secondary_button" in theme:
            self.style.configure(
                "Secondary.TButton",
                background=theme["secondary_button"],
                foreground="#FFFFFF",
            )
            self.style.map(
                "Secondary.TButton", background=[("active", theme["secondary_hover"])]
            )

        # Entry and Combobox styles
        self.style.configure(
            "TEntry",
            fieldbackground=theme["entry_bg"],
            foreground=theme["entry_fg"],
            bordercolor=theme["border"],
            lightcolor=theme["border"],
            darkcolor=theme["border"],
        )
        self.style.configure(
            "TCombobox",
            fieldbackground=theme["entry_bg"],
            foreground=theme["entry_fg"],
            background=theme["button_bg"],
            bordercolor=theme["border"],
            arrowcolor=theme["fg"],
            selectbackground=theme["primary_button"],
        )
        self.style.map(
            "TCombobox",
            fieldbackground=[("readonly", theme["entry_bg"])],
            foreground=[("readonly", theme["entry_fg"])],
        )

        # Notebook styles
        self.style.configure(
            "TNotebook", background=theme["bg"], bordercolor=theme["border"]
        )
        self.style.configure(
            "TNotebook.Tab",
            background=theme["button_bg"],
            foreground=theme["fg"],
            padding=[10, 5],
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", theme["primary_button"])],
            foreground=[("selected", "#FFFFFF")],
        )

        # Radiobutton and Checkbutton styles
        self.style.configure(
            "TRadiobutton", background=theme["bg"], foreground=theme["fg"]
        )
        self.style.configure(
            "TCheckbutton", background=theme["bg"], foreground=theme["fg"]
        )

        # Update canvases
        if hasattr(self, "canvas"):
            self.canvas.configure(bg=theme["canvas_bg"])
        if hasattr(self, "status_text"):
            self.status_text.configure(
                bg=theme["text_bg"], fg=theme["fg"], insertbackground=theme["fg"]
            )
        if hasattr(self, "help_textbox"):
            self.help_textbox.configure(
                bg=theme["text_bg"], fg=theme["fg"], insertbackground=theme["fg"]
            )
        if hasattr(self, "plots_canvas"):
            self.plots_canvas.configure(bg=theme["canvas_bg"])
        if hasattr(self, "schedule_canvas"):
            self.schedule_canvas.configure(bg=theme["canvas_bg"])
        if hasattr(self, "viewer_plots_canvas"):
            self.viewer_plots_canvas.configure(bg=theme["canvas_bg"])

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill="both", expand=True)

        # Top bar for theme toggle and title
        top_bar = ttk.Frame(main_frame)
        top_bar.pack(fill="x", pady=(0, 10))

        title_label = ttk.Label(
            top_bar,
            text="🎓 AI-Hoshino Course Scheduler",
            font=("Segoe UI", 16, "bold"),
        )
        title_label.pack(side="left", padx=10)

        theme_button = ttk.Button(
            top_bar, text="🌓 Toggle Theme", command=self.toggle_theme, style="TButton"
        )
        theme_button.pack(side="right", padx=5, ipady=5)

        # Notebook for pages
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)

        # --- Page 1: Scheduler (Main) ---
        self.scheduler_page = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.scheduler_page, text="📅 Scheduler")
        self.create_scheduler_page()

        # --- Page 2: Schedule Viewer ---
        self.schedule_page = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.schedule_page, text="📋 Schedule Viewer")
        self.create_schedule_viewer_page()

        # --- Page 3: Help ---
        self.help_page = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.help_page, text="❓ Help")
        self.create_help_page()

    def create_scheduler_page(self):
        # Main horizontal layout: Left sidebar (fixed) + Right content area
        container = ttk.Frame(self.scheduler_page)
        container.pack(fill="both", expand=True)

        # --- LEFT SIDEBAR: Controls (Fixed width, no resizing) ---
        sidebar_frame = ttk.Frame(container, padding="10", width=320)
        sidebar_frame.pack(side="left", fill="y")
        sidebar_frame.pack_propagate(False)  # Prevent resizing

        # File Upload Section
        file_section = ttk.LabelFrame(sidebar_frame, text="📁 Input File", padding="10")
        file_section.pack(fill="x", pady=(0, 10))

        self.file_label = ttk.Label(file_section, text="No file loaded", wraplength=250)
        self.file_label.pack(fill="x", pady=(0, 5))

        load_button = ttk.Button(
            file_section,
            text="Load JSON File",
            command=self.load_file_for_scheduler,
            style="TButton",
        )
        load_button.pack(fill="x", ipady=3)

        # Algorithm Selection
        algo_section = ttk.LabelFrame(sidebar_frame, text="⚙️ Algorithm", padding="10")
        algo_section.pack(fill="x", pady=(0, 10))

        algorithms = [
            ("Hill Climbing", "hill_climbing"),
            ("Simulated Annealing", "simulated_annealing"),
            ("Genetic Algorithm", "genetic"),
        ]

        for text, value in algorithms:
            rb = ttk.Radiobutton(
                algo_section,
                text=text,
                variable=self.selected_algorithm,
                value=value,
                command=self.update_parameter_panel,
            )
            rb.pack(anchor="w", pady=2)

        # Parameters Section
        self.param_section = ttk.LabelFrame(
            sidebar_frame, text="🔧 Parameters", padding="10"
        )
        self.param_section.pack(fill="both", expand=True, pady=(0, 10))

        # This will be dynamically filled
        self.param_frame = ttk.Frame(self.param_section)
        self.param_frame.pack(fill="both", expand=True)
        self.update_parameter_panel()

        # Options
        options_section = ttk.LabelFrame(sidebar_frame, text="📊 Options", padding="10")
        options_section.pack(fill="x", pady=(0, 10))

        show_plots_cb = ttk.Checkbutton(
            options_section,
            text="Show Plots",
            variable=self.show_plots,
            command=self.toggle_plot_panel,
        )
        show_plots_cb.pack(anchor="w")

        # Run and Cancel Buttons
        button_frame = ttk.Frame(sidebar_frame)
        button_frame.pack(fill="x")

        self.run_button = ttk.Button(
            button_frame,
            text="▶️ Run",
            command=self.run_algorithm,
            style="Primary.TButton",
        )
        self.run_button.pack(fill="x", ipady=10, pady=(0, 5))

        self.cancel_button = ttk.Button(
            button_frame,
            text="⏹️ Cancel",
            command=self.cancel_algorithm,
            style="TButton",
            state=tk.DISABLED,
        )
        self.cancel_button.pack(fill="x", ipady=10)

        # --- RIGHT CONTENT AREA ---
        content_frame = ttk.Frame(container)
        content_frame.pack(side="left", fill="both", expand=True)

        # Results Section
        results_frame = ttk.LabelFrame(content_frame, text="📈 Results", padding="10")
        results_frame.pack(fill="both", expand=True, pady=(0, 5))

        # Status text area
        self.status_text = scrolledtext.ScrolledText(
            results_frame, height=10, font=("Consolas", 10), wrap=tk.WORD
        )
        self.status_text.pack(fill="both", expand=True)
        self.status_text.insert(
            "1.0", "Load a file and select an algorithm to begin.\n"
        )
        self.status_text.config(state=tk.DISABLED)

        # Plots Section (initially hidden)
        self.plots_frame = ttk.LabelFrame(
            content_frame, text="📊 Visualization", padding="10"
        )
        if self.show_plots.get():
            self.plots_frame.pack(fill="both", expand=True)

        # Scrollable canvas for plots
        self.plots_canvas = tk.Canvas(self.plots_frame, highlightthickness=0)
        plots_scrollbar = ttk.Scrollbar(
            self.plots_frame, orient="vertical", command=self.plots_canvas.yview
        )
        self.plots_display_frame = ttk.Frame(self.plots_canvas)

        self.plots_canvas.configure(yscrollcommand=plots_scrollbar.set)
        plots_scrollbar.pack(side="right", fill="y")
        self.plots_canvas.pack(side="left", fill="both", expand=True)

        self.plots_canvas.create_window(
            (0, 0), window=self.plots_display_frame, anchor="nw"
        )
        self.plots_display_frame.bind(
            "<Configure>",
            lambda e: self.plots_canvas.configure(
                scrollregion=self.plots_canvas.bbox("all")
            ),
        )

    def create_help_page(self):
        theme = self.dark_theme if self.dark_mode else self.light_theme
        self.help_textbox = scrolledtext.ScrolledText(
            self.help_page,
            font=("Consolas", 10),  # Monospace font for better formatting
            wrap=tk.WORD,
            padx=20,
            pady=20,
            bg=theme["text_bg"],
            fg=theme["fg"],
            insertbackground=theme["fg"],
            relief=tk.FLAT,
            borderwidth=0,
        )
        self.help_textbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.help_textbox.insert("1.0", HELP_TEXT)
        self.help_textbox.config(state=tk.DISABLED)

    def create_schedule_viewer_page(self):
        # Info label at top
        info_label = ttk.Label(
            self.schedule_page,
            text="📋 View the optimized schedule here after running an algorithm",
            font=("Segoe UI", 12),
        )
        info_label.pack(pady=10)

        # Main horizontal paned window for schedule and plots
        main_paned = ttk.PanedWindow(self.schedule_page, orient=tk.HORIZONTAL)
        main_paned.pack(fill="both", expand=True)

        # LEFT: Schedule display area with minimum width
        schedule_container = ttk.Frame(main_paned, width=400)
        main_paned.add(schedule_container, weight=2)

        # Canvas for scrolling schedule (vertical only)
        self.schedule_canvas = tk.Canvas(schedule_container, highlightthickness=0)
        self.schedule_canvas.pack(side="left", fill="both", expand=True)

        # Vertical scrollbar for schedule
        schedule_scrollbar = ttk.Scrollbar(
            schedule_container, orient="vertical", command=self.schedule_canvas.yview
        )
        schedule_scrollbar.pack(side="right", fill="y")
        self.schedule_canvas.configure(yscrollcommand=schedule_scrollbar.set)

        # Frame inside canvas for schedule
        self.schedule_display_frame = ttk.Frame(self.schedule_canvas)
        self.schedule_canvas.create_window(
            (0, 0), window=self.schedule_display_frame, anchor="nw"
        )
        self.schedule_display_frame.bind(
            "<Configure>", self.on_schedule_frame_configure
        )

        # RIGHT: Plots display area with minimum width
        plots_container = ttk.LabelFrame(
            main_paned, text="📊 Visualization", padding="10", width=300
        )
        main_paned.add(plots_container, weight=1)

        # Frame to hold canvas and scrollbars
        plots_scroll_frame = ttk.Frame(plots_container)
        plots_scroll_frame.pack(fill="both", expand=True)

        # Canvas for scrolling plots
        self.viewer_plots_canvas = tk.Canvas(plots_scroll_frame, highlightthickness=0)
        self.viewer_plots_canvas.grid(row=0, column=0, sticky="nsew")

        # Vertical scrollbar for plots
        plots_v_scrollbar = ttk.Scrollbar(
            plots_scroll_frame,
            orient="vertical",
            command=self.viewer_plots_canvas.yview,
        )
        plots_v_scrollbar.grid(row=0, column=1, sticky="ns")

        # Horizontal scrollbar for plots
        plots_h_scrollbar = ttk.Scrollbar(
            plots_scroll_frame,
            orient="horizontal",
            command=self.viewer_plots_canvas.xview,
        )
        plots_h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Configure canvas scrolling
        self.viewer_plots_canvas.configure(
            yscrollcommand=plots_v_scrollbar.set, xscrollcommand=plots_h_scrollbar.set
        )

        # Configure grid weights for proper resizing
        plots_scroll_frame.grid_rowconfigure(0, weight=1)
        plots_scroll_frame.grid_columnconfigure(0, weight=1)

        # Frame inside canvas for plots
        self.viewer_plots_display_frame = ttk.Frame(self.viewer_plots_canvas)
        self.viewer_plots_canvas.create_window(
            (0, 0), window=self.viewer_plots_display_frame, anchor="nw"
        )
        self.viewer_plots_display_frame.bind(
            "<Configure>",
            lambda e: self.viewer_plots_canvas.configure(
                scrollregion=self.viewer_plots_canvas.bbox("all")
            ),
        )

    def on_frame_configure(self, event=None):
        # Legacy method - kept for compatibility
        if hasattr(self, "canvas"):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_schedule_frame_configure(self, event=None):
        self.schedule_canvas.configure(scrollregion=self.schedule_canvas.bbox("all"))

    def load_file_for_scheduler(self):
        file_path = filedialog.askopenfilename(
            title="Select Input JSON File",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*")),
        )
        if not file_path:
            return

        try:
            self.classes, self.rooms, self.students = load_input(file_path)
            self.current_file_path = file_path
            import os

            filename = os.path.basename(file_path)
            self.file_label.config(
                text=f"✓ {filename}\n{len(self.classes)} classes, {len(self.rooms)} rooms"
            )
            self.log_status(f"Loaded file: {filename}\n")
            self.log_status(f"  - Classes: {len(self.classes)}\n")
            self.log_status(f"  - Rooms: {len(self.rooms)}\n")
            self.log_status(f"  - Students: {len(self.students)}\n\n")
        except (FileNotFoundError, ValueError) as e:
            messagebox.showerror("Error", f"Failed to load file:\n{e}")

    def update_parameter_panel(self):
        # Clear existing parameters
        for widget in self.param_frame.winfo_children():
            widget.destroy()

        algo = self.selected_algorithm.get()
        params = self.algorithm_params[algo]

        if algo == "hill_climbing":
            # Variant
            ttk.Label(self.param_frame, text="Variant:").grid(
                row=0, column=0, sticky="w", pady=2
            )
            variant_combo = ttk.Combobox(
                self.param_frame,
                textvariable=params["variant"],
                state="readonly",
                width=18,
            )
            variant_combo["values"] = [
                "stochastic",
                "steepest_ascent",
                "sideways_move",
                "random_restart",
            ]
            variant_combo.grid(row=0, column=1, pady=2)
            # Bind callback to update parameter states when variant changes
            variant_combo.bind("<<ComboboxSelected>>", self.update_hc_param_states)

            # Max Iterations (always enabled)
            ttk.Label(self.param_frame, text="Max Iterations:").grid(
                row=1, column=0, sticky="w", pady=2
            )
            ttk.Entry(
                self.param_frame, textvariable=params["max_iterations"], width=20
            ).grid(row=1, column=1, pady=2)

            # Max Sideways Moves (for sideways_move only)
            self.hc_param_widgets["max_sideways_label"] = ttk.Label(
                self.param_frame, text="Max Sideways:"
            )
            self.hc_param_widgets["max_sideways_label"].grid(
                row=2, column=0, sticky="w", pady=2
            )
            self.hc_param_widgets["max_sideways_entry"] = ttk.Entry(
                self.param_frame, textvariable=params["max_sideways_moves"], width=20
            )
            self.hc_param_widgets["max_sideways_entry"].grid(row=2, column=1, pady=2)

            # Max Restarts (for random_restart only)
            self.hc_param_widgets["max_restarts_label"] = ttk.Label(
                self.param_frame, text="Max Restarts:"
            )
            self.hc_param_widgets["max_restarts_label"].grid(
                row=3, column=0, sticky="w", pady=2
            )
            self.hc_param_widgets["max_restarts_entry"] = ttk.Entry(
                self.param_frame, textvariable=params["max_restarts"], width=20
            )
            self.hc_param_widgets["max_restarts_entry"].grid(row=3, column=1, pady=2)

            # Initialize parameter states based on current variant
            self.update_hc_param_states()

        elif algo == "simulated_annealing":
            # Initial Temperature
            ttk.Label(self.param_frame, text="Initial Temp:").grid(
                row=0, column=0, sticky="w", pady=2
            )
            ttk.Entry(
                self.param_frame, textvariable=params["initial_temp"], width=20
            ).grid(row=0, column=1, pady=2)

            # Cooling Rate
            ttk.Label(self.param_frame, text="Cooling Rate:").grid(
                row=1, column=0, sticky="w", pady=2
            )
            ttk.Entry(
                self.param_frame, textvariable=params["cooling_rate"], width=20
            ).grid(row=1, column=1, pady=2)

            # Max Iterations
            ttk.Label(self.param_frame, text="Max Iterations:").grid(
                row=2, column=0, sticky="w", pady=2
            )
            ttk.Entry(
                self.param_frame, textvariable=params["max_iterations"], width=20
            ).grid(row=2, column=1, pady=2)

        elif algo == "genetic":
            # Population Size
            ttk.Label(self.param_frame, text="Population Size:").grid(
                row=0, column=0, sticky="w", pady=2
            )
            ttk.Entry(
                self.param_frame, textvariable=params["population_size"], width=20
            ).grid(row=0, column=1, pady=2)

            # Generations
            ttk.Label(self.param_frame, text="Generations:").grid(
                row=1, column=0, sticky="w", pady=2
            )
            ttk.Entry(
                self.param_frame, textvariable=params["generations"], width=20
            ).grid(row=1, column=1, pady=2)

    def update_hc_param_states(self, *args):
        """Enable/disable Hill Climbing parameters based on selected variant."""
        variant = self.algorithm_params["hill_climbing"]["variant"].get()

        # Define which parameters are needed for each variant
        # stochastic: needs nothing extra
        # steepest_ascent: evaluates all neighbors
        # sideways_move: needs max_sideways_moves
        # random_restart: needs max_restarts

        # Determine enabled states
        enable_max_sideways = variant == "sideways_move"
        enable_max_restarts = variant == "random_restart"

        # Update widget states
        state_max_sideways = "normal" if enable_max_sideways else "disabled"
        state_max_restarts = "normal" if enable_max_restarts else "disabled"

        # Apply states to widgets if they exist
        if self.hc_param_widgets["max_sideways_entry"]:
            self.hc_param_widgets["max_sideways_entry"].config(state=state_max_sideways)
            fg_color = (
                self.dark_theme["fg"]
                if enable_max_sideways
                else self.dark_theme["disabled_fg"]
            )
            if self.dark_mode:
                self.hc_param_widgets["max_sideways_label"].config(foreground=fg_color)

        if self.hc_param_widgets["max_restarts_entry"]:
            self.hc_param_widgets["max_restarts_entry"].config(state=state_max_restarts)
            fg_color = (
                self.dark_theme["fg"]
                if enable_max_restarts
                else self.dark_theme["disabled_fg"]
            )
            if self.dark_mode:
                self.hc_param_widgets["max_restarts_label"].config(foreground=fg_color)

    def toggle_plot_panel(self):
        # This will be handled in run_algorithm - plots shown dynamically
        pass

    def log_status(self, message):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message)
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.update_idletasks()

    def run_algorithm(self):
        if not self.classes or not self.rooms:
            messagebox.showwarning("No Data", "Please load an input file first.")
            return

        if self.is_running:
            messagebox.showinfo(
                "Running", "An algorithm is already running. Please wait."
            )
            return

        # Clear previous plots from both locations
        for widget in self.plots_display_frame.winfo_children():
            widget.destroy()
        for widget in self.viewer_plots_display_frame.winfo_children():
            widget.destroy()
        self.plot_images = []  # Clear image references

        # Clear status
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete("1.0", tk.END)
        self.status_text.config(state=tk.DISABLED)

        # Enable cancel, disable run
        self.is_running = True
        self.cancel_requested = False
        self.run_button.config(state=tk.DISABLED, text="⏳ Running...")
        self.cancel_button.config(state=tk.NORMAL)

        # Run algorithm in separate thread
        thread = threading.Thread(target=self._execute_algorithm, daemon=True)
        thread.start()

    def cancel_algorithm(self):
        if self.is_running:
            self.cancel_requested = True
            self.log_status("\n⚠️ Cancellation requested...\n")
            self.log_status("   Note: Algorithm will stop after current iteration completes.\n")
            self.log_status("   This may take a few seconds for large problems.\n")
            self.cancel_button.config(state=tk.DISABLED, text="⏳ Stopping...")

    def _execute_algorithm(self):
        try:
            algo = self.selected_algorithm.get()
            params = self.algorithm_params[algo]

            self.log_status("=" * 70 + "\n")
            self.log_status(f"RUNNING {algo.upper().replace('_', ' ')} ALGORITHM\n")
            self.log_status("=" * 70 + "\n\n")

            objective_func = ObjectiveFunction(
                student_conflict=True, room_conflict=True, capacity=True
            )

            if algo == "hill_climbing":
                self._run_hill_climbing(objective_func, params)
            elif algo == "simulated_annealing":
                self._run_simulated_annealing(objective_func, params)
            elif algo == "genetic":
                self._run_genetic_algorithm(params)

        except Exception as e:
            self.log_status(f"\n❌ ERROR: {str(e)}\n")
            import traceback

            self.log_status(traceback.format_exc())
        finally:
            self.is_running = False
            self.cancel_requested = False
            self.run_button.config(state=tk.NORMAL, text="▶️ Run")
            self.cancel_button.config(state=tk.DISABLED, text="⏹️ Cancel")

    def _run_hill_climbing(self, objective_func, params):
        if self.cancel_requested:
            return

        self.log_status(f"Configuration:\n")
        self.log_status(f"  Variant: {params['variant'].get()}\n")
        self.log_status(f"  Max Iterations: {params['max_iterations'].get()}\n")

        # Create initial state
        initial_state = State()
        initial_state.random_fill(self.classes, self.rooms)
        initial_penalty = objective_func.calculate(initial_state)

        self.log_status(f"\nInitial State (Random Schedule):\n")
        self.log_status(f"Initial Penalty: {initial_penalty:.2f}\n")
        self.log_status("-" * 70 + "\n")

        if self.cancel_requested:
            return

        hc = HillClimbing(
            objective_function=objective_func, rooms=self.rooms, classes=self.classes
        )

        start_time = time.time()
        best_state, results = hc.solve(
            initial_state=initial_state,
            variant=params["variant"].get(),
            max_iterations=params["max_iterations"].get(),
            max_sideways_moves=params["max_sideways_moves"].get(),
            max_restarts=params["max_restarts"].get(),
            restart_variant="steepest_ascent",
        )
        duration = time.time() - start_time

        if self.cancel_requested:
            self.log_status("\n⚠️ Algorithm cancelled by user.\n")
            return

        # Display results
        self.log_status("\n" + "=" * 70 + "\n")
        self.log_status("RESULTS\n")
        self.log_status("=" * 70 + "\n")
        self.log_status(f"Initial Penalty:  {initial_penalty:.2f}\n")
        self.log_status(f"Best Penalty:     {results['best_penalty']:.2f}\n")
        improvement = initial_penalty - results["best_penalty"]
        improvement_pct = (
            (improvement / initial_penalty * 100) if initial_penalty > 0 else 0
        )
        self.log_status(
            f"Improvement:      {improvement:.2f} ({improvement_pct:.1f}%)\n"
        )
        self.log_status(f"Iterations:       {results['iterations']}\n")
        self.log_status(f"Duration:         {duration:.2f} seconds\n")

        if params["variant"].get() == "random_restart":
            self.log_status(f"Restarts:         {results['restarts']}\n")

        self.log_status("=" * 70 + "\n")

        # Store state and display
        self.state = best_state
        self.algorithm_results = results
        self.after(0, self.display_all_schedules)

        # Generate and display plots
        if self.show_plots.get():
            try:
                fig = hc.plot_results(
                    results, show=False
                )  # Don't show popup windows in GUI
                self.after(0, lambda: self._display_plot(fig, "Hill Climbing Progress"))
            except Exception as e:
                self.log_status(f"\n⚠️ Could not generate plot: {e}\n")

        # Switch to Schedule Viewer tab to show results
        self.after(100, lambda: self.notebook.select(self.schedule_page))

    def _run_simulated_annealing(self, objective_func, params):
        if self.cancel_requested:
            return

        self.log_status(f"Configuration:\n")
        self.log_status(f"  Initial Temperature: {params['initial_temp'].get()}\n")
        self.log_status(f"  Cooling Rate: {params['cooling_rate'].get()}\n")
        self.log_status(f"  Max Iterations: {params['max_iterations'].get()}\n")

        # Create and display initial state info
        initial_state = State()
        initial_state.random_fill(self.classes, self.rooms)
        initial_penalty = objective_func.calculate(initial_state)

        self.log_status(f"\nInitial State (Random Schedule):\n")
        self.log_status(f"Initial Penalty: {initial_penalty:.2f}\n")
        self.log_status("-" * 70 + "\n")

        if self.cancel_requested:
            return

        sa = SimulatedAnnealing(
            classes=self.classes,
            rooms=self.rooms,
            objective_function=objective_func,
            initial_temp=params["initial_temp"].get(),
            cooling_rate=params["cooling_rate"].get(),
            min_temp=0.01,
            max_iterations=params["max_iterations"].get(),
        )

        start_time = time.time()
        best_state, results = sa.run(verbose=False)
        duration = time.time() - start_time

        if self.cancel_requested:
            self.log_status("\n⚠️ Algorithm cancelled by user.\n")
            return

        # Display results
        self.log_status("\n" + "=" * 70 + "\n")
        self.log_status("RESULTS\n")
        self.log_status("=" * 70 + "\n")
        self.log_status(f"Initial Penalty:  {results['initial_penalty']:.2f}\n")
        self.log_status(f"Best Penalty:     {results['best_penalty']:.2f}\n")
        self.log_status(f"Final Penalty:    {results['final_penalty']:.2f}\n")
        improvement = results["initial_penalty"] - results["best_penalty"]
        improvement_pct = (
            (improvement / results["initial_penalty"] * 100)
            if results["initial_penalty"] > 0
            else 0
        )
        self.log_status(
            f"Improvement:      {improvement:.2f} ({improvement_pct:.1f}%)\n"
        )
        self.log_status(f"Iterations:       {results['iterations']}\n")
        self.log_status(f"Duration:         {duration:.2f} seconds\n")
        self.log_status(f"Local Optima:     {results['local_optima_count']}\n")
        self.log_status("=" * 70 + "\n")

        # Store state and display
        self.state = best_state
        self.algorithm_results = results
        self.after(0, self.display_all_schedules)

        # Generate and display plots
        if self.show_plots.get():
            try:
                figures = sa.plot_results(
                    results, show=False
                )  # Don't show popup windows in GUI
                # Display each figure independently
                for i, fig in enumerate(figures):
                    title = f"SA Plot {i + 1}: " + (
                        "Objective Function" if i == 0 else "Acceptance Probability"
                    )
                    self.after(0, lambda f=fig, t=title: self._display_plot(f, t))
            except Exception as e:
                self.log_status(f"\n⚠️ Could not generate plots: {e}\n")

        # Switch to Schedule Viewer tab to show results
        self.after(100, lambda: self.notebook.select(self.schedule_page))

    def _run_genetic_algorithm(self, params):
        if self.cancel_requested:
            return

        self.log_status(f"Configuration:\n")
        self.log_status(f"  Population Size: {params['population_size'].get()}\n")
        self.log_status(f"  Generations: {params['generations'].get()}\n\n")

        # Create and display initial state
        initial_state = State()
        initial_state.random_fill(self.classes, self.rooms)
        objective_func = ObjectiveFunction()
        initial_penalty = objective_func.calculate(initial_state)

        self.log_status(f"Initial State (Random Schedule):\n")
        self.log_status(f"Initial Penalty: {initial_penalty:.2f}\n")
        self.log_status("-" * 70 + "\n")

        if self.cancel_requested:
            return

        start_time = time.time()

        # Use GeneticAlgorithm directly to get figure back
        from .algorithms.genetic import GeneticAlgorithm

        ga = GeneticAlgorithm(
            population_size=params["population_size"].get(),
            generations=params["generations"].get(),
        )

        best_state, fitness_history, fig = ga.optimize(
            classes=self.classes,
            rooms=self.rooms,
            show_plot=False,  # Don't show popup windows in GUI
        )

        duration = time.time() - start_time

        if self.cancel_requested:
            self.log_status("\n⚠️ Algorithm cancelled by user.\n")
            return

        best_penalty = objective_func.calculate(best_state)

        # Display results
        self.log_status("\n" + "=" * 70 + "\n")
        self.log_status("RESULTS\n")
        self.log_status("=" * 70 + "\n")
        self.log_status(f"Initial Penalty:  {initial_penalty:.2f}\n")
        self.log_status(f"Best Penalty:     {best_penalty:.2f}\n")
        improvement = initial_penalty - best_penalty
        improvement_pct = (
            (improvement / initial_penalty * 100) if initial_penalty > 0 else 0
        )
        self.log_status(
            f"Improvement:      {improvement:.2f} ({improvement_pct:.1f}%)\n"
        )
        self.log_status(f"Generations:      {params['generations'].get()}\n")
        self.log_status(f"Population Size:  {params['population_size'].get()}\n")
        self.log_status(f"Duration:         {duration:.2f} seconds\n")
        self.log_status("=" * 70 + "\n")

        # Store state and display
        self.state = best_state
        self.after(0, self.display_all_schedules)

        # Display plot in GUI
        if self.show_plots.get() and fig is not None:
            try:
                self.after(
                    0, lambda: self._display_plot(fig, "Genetic Algorithm Progress")
                )
            except Exception as e:
                self.log_status(f"\n⚠️ Could not generate plot: {e}\n")

        # Switch to Schedule Viewer tab to show results
        self.after(100, lambda: self.notebook.select(self.schedule_page))

    def _display_plot(self, fig, title):
        if fig is None:
            self.log_status(f"⚠️ Plot '{title}' is None, skipping display\n")
            return

        try:
            self.log_status(f"📊 Displaying plot: {title}\n")

            # Display plots in the schedule viewer page (right side)
            plot_frame = ttk.LabelFrame(
                self.viewer_plots_display_frame, text=title, padding="5"
            )
            plot_frame.pack(fill="both", expand=True, pady=5, padx=5)

            # Calculate target width - use most of the available space
            self.viewer_plots_display_frame.update_idletasks()
            frame_width = self.viewer_plots_display_frame.winfo_width()

            # Use a reasonable default if frame not fully initialized yet
            if frame_width <= 1:
                frame_width = 600  # Increased from 450

            # Use 98% of available width for larger plots
            target_width = int(frame_width * 0.98)

            # Calculate height based on figure's aspect ratio
            fig_width, fig_height = fig.get_size_inches()
            aspect_ratio = fig_height / fig_width
            target_height = int(target_width * aspect_ratio)

            # Set reasonable min/max dimensions
            min_width = 500
            max_width = 1200
            min_height = 300
            max_height = 700  # Increased from 400

            # Apply constraints
            if target_width < min_width:
                target_width = min_width
                target_height = int(target_width * aspect_ratio)
            elif target_width > max_width:
                target_width = max_width
                target_height = int(target_width * aspect_ratio)

            if target_height < min_height:
                target_height = min_height
                target_width = int(target_height / aspect_ratio)
            elif target_height > max_height:
                target_height = max_height
                target_width = int(target_height / aspect_ratio)

            # Set figure size for rendering with higher DPI for better quality
            dpi = 120  # Increased from 100 for sharper text
            fig.set_size_inches(target_width / dpi, target_height / dpi)

            # Render figure to buffer as PNG - always use white background
            buf = io.BytesIO()
            fig.savefig(
                buf,
                format="png",
                dpi=dpi,
                bbox_inches="tight",
                facecolor="white",  # Always white background
                edgecolor="none",
            )
            buf.seek(0)

            # Load and resize image
            pil_image = Image.open(buf)

            # Ensure image fits within target dimensions
            if pil_image.width > target_width or pil_image.height > target_height:
                pil_image.thumbnail((target_width, target_height), Image.LANCZOS)

            # Convert to PhotoImage
            photo_image = ImageTk.PhotoImage(pil_image)

            # Display as static image label - white background
            image_label = tk.Label(plot_frame, image=photo_image, bg="white", bd=0)
            image_label.pack(anchor="center")

            # Store reference to prevent garbage collection
            self.plot_images.append(photo_image)

            # Clean up
            plt.close(fig)
            buf.close()

            self.log_status(f"✓ Plot '{title}' displayed successfully\n")

        except Exception as e:
            import traceback

            self.log_status(f"\n⚠️ Error displaying plot '{title}': {e}\n")
            self.log_status(f"Traceback: {traceback.format_exc()}\n")

    def display_all_schedules(self):
        # Clear schedule display efficiently
        for widget in self.schedule_display_frame.winfo_children():
            widget.destroy()

        # Clear plots in viewer
        for widget in self.viewer_plots_display_frame.winfo_children():
            widget.destroy()

        # Clear image references
        self.plot_images.clear()

        if not self.state:
            no_schedule_label = ttk.Label(
                self.schedule_display_frame,
                text="No schedule to display. Run an algorithm first.",
                font=("Segoe UI", 12),
            )
            no_schedule_label.pack(pady=50)
            return

        # Switch to schedule viewer tab
        self.notebook.select(self.schedule_page)

        # Add summary at top
        summary_frame = ttk.Frame(self.schedule_display_frame, padding="10")
        summary_frame.pack(fill="x", pady=(0, 20))

        objective_func = ObjectiveFunction()
        penalty = objective_func.calculate(self.state)

        ttk.Label(
            summary_frame,
            text=f"📊 Final Penalty: {penalty:.2f}",
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w")

        if self.algorithm_results:
            if "iterations" in self.algorithm_results:
                ttk.Label(
                    summary_frame,
                    text=f"Iterations: {self.algorithm_results['iterations']}",
                    font=("Segoe UI", 11),
                ).pack(anchor="w")

        ttk.Separator(summary_frame, orient="horizontal").pack(fill="x", pady=10)

        # Optimize: Sort once
        sorted_rooms = sorted(self.rooms.values(), key=lambda r: r.code)

        # Optimize: Batch widget creation
        for room in sorted_rooms:
            self.create_schedule_grid(room)

        # Update scroll region once after all widgets created
        self.after(100, self.on_schedule_frame_configure)

    def create_schedule_grid(self, room):
        # Frame for the room schedule
        room_frame = ttk.Frame(self.schedule_display_frame, padding="10")
        room_frame.pack(pady=20, padx=20, fill="x")

        # Room code label
        room_label = ttk.Label(
            room_frame, text=f"Kode ruang: {room.code}", style="Room.TLabel"
        )
        room_label.pack(pady=(0, 10), anchor="w")

        # Grid frame
        grid_frame = ttk.Frame(room_frame)
        grid_frame.pack(fill="x", expand=True)

        # Optimize: Pre-compute schedule data first
        schedule = {}  # (day, hour) -> class_code
        day_map = {
            "MONDAY": 1,
            "TUESDAY": 2,
            "WEDNESDAY": 3,
            "THURSDAY": 4,
            "FRIDAY": 5,
        }

        for meeting in self.state.meetings:
            if meeting.room.code == room.code:
                day_index = day_map.get(meeting.time_slot.day.name)
                if day_index is not None:
                    for hour in range(
                        meeting.time_slot.start_hour, meeting.time_slot.end_hour
                    ):
                        schedule[(day_index, hour)] = meeting.course_class.code

        # Header
        headers = ["Jam", "Senin", "Selasa", "Rabu", "Kamis", "Jumat"]
        for i, header in enumerate(headers):
            label = ttk.Label(
                grid_frame, text=header, style="Header.TLabel", anchor="center"
            )
            label.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)

        # Time slots and data combined for efficiency
        for hour in range(7, 18):
            row = hour - 6
            # Time label
            ttk.Label(
                grid_frame, text=f"{hour:02d}:00", style="Time.TLabel", anchor="center"
            ).grid(row=row, column=0, sticky="nsew", padx=1, pady=1)

            # Schedule cells for all days
            for day in range(1, 6):
                class_code = schedule.get((day, hour), "")
                ttk.Label(
                    grid_frame, text=class_code, style="Cell.TLabel", anchor="center"
                ).grid(row=row, column=day, sticky="nsew", padx=1, pady=1)

        # Configure grid weights once
        for i in range(6):
            grid_frame.grid_columnconfigure(i, weight=1, minsize=120)
        for i in range(12):
            grid_frame.grid_rowconfigure(i, weight=1, minsize=40)


if __name__ == "__main__":
    app = SchedulerGUI()
    app.mainloop()
