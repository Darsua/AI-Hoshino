import random
import copy
from typing import List, Dict, Tuple, Optional
import matplotlib
import matplotlib.pyplot as plt
from src.main.state import State
from src.main.objective import ObjectiveFunction
from src.models import TimeSlot, CourseClass, Room


class GeneticAlgorithm:
    def __init__(self, population_size: int = 20, generations: int = 100):
        """
        Initialize the Genetic Algorithm for course scheduling.

        Args:
            population_size: Number of individuals in each generation
            generations: Number of generations to evolve
        """
        self.population_size = population_size
        self.generations = generations
        self.objective_function = ObjectiveFunction()

        # Performance optimizations
        self._fitness_cache: Dict[int, float] = {}
        self._penalty_cache: Dict[int, float] = {}

        # Will be set during optimization
        self.classes: Dict[str, CourseClass] = {}
        self.rooms: Dict[str, Room] = {}
        self.room_list: List[Room] = []

    def _get_state_hash(self, state: State) -> int:
        """Generate a hash for a state to enable caching."""
        # Create a simple hash based on meetings
        hash_data = []
        for meeting in state.meetings:
            hash_data.append(
                (
                    meeting.course_class.code,
                    meeting.time_slot.day.value,
                    meeting.time_slot.start_hour,
                    meeting.time_slot.end_hour,
                    meeting.room.code,
                )
            )
        return hash(tuple(sorted(hash_data)))

    def initialize_population(
        self, classes: Dict[str, CourseClass], rooms: Dict[str, Room]
    ) -> List[State]:
        """Create initial population of random schedules."""
        if not classes or not rooms:
            raise ValueError("Cannot initialize population with empty classes or rooms")

        population = []
        self.classes = classes
        self.rooms = rooms
        self.room_list = list(rooms.values())

        for _ in range(self.population_size):
            individual = State()
            individual.random_fill(classes, rooms)
            population.append(individual)

        return population

    def evaluate_fitness(self, individual: State) -> float:
        """
        Evaluate fitness of an individual with caching.
        """
        state_hash = self._get_state_hash(individual)

        # Check cache first
        if state_hash in self._fitness_cache:
            return self._fitness_cache[state_hash]

        penalty = self.objective_function.calculate(individual)
        # Convert penalty to fitness (higher fitness is better)
        fitness = 1.0 / (1.0 + penalty)

        # Cache both fitness and penalty
        self._fitness_cache[state_hash] = fitness
        self._penalty_cache[state_hash] = penalty

        return fitness

    def get_penalty(self, individual: State) -> float:
        """Get penalty with caching."""
        state_hash = self._get_state_hash(individual)

        if state_hash in self._penalty_cache:
            return self._penalty_cache[state_hash]

        penalty = self.objective_function.calculate(individual)
        self._penalty_cache[state_hash] = penalty

        return penalty

    def tournament_selection(
        self, population: List[State], fitnesses: List[float]
    ) -> int:
        """Select an individual using tournament selection. Returns index."""
        idx1, idx2 = random.sample(range(len(population)), 2)
        return idx1 if fitnesses[idx1] > fitnesses[idx2] else idx2

    def crossover(self, parent1: State, parent2: State) -> Tuple[State, State]:
        """
        Perform crossover between two parents to create two offspring.
        Optimized to minimize object creation.
        """
        # Get all unique course codes from both parents
        all_courses = set()
        for meeting in parent1.meetings:
            all_courses.add(meeting.course_class.code)
        for meeting in parent2.meetings:
            all_courses.add(meeting.course_class.code)

        # Convert to list for sampling (faster than set operations in loop)
        course_list = list(all_courses)
        split_point = len(course_list) // 2
        courses_from_parent1 = set(course_list[:split_point])

        # Pre-allocate children
        child1 = State()
        child2 = State()
        child1.meetings = []
        child2.meetings = []

        # Build children more efficiently
        for meeting in parent1.meetings:
            if meeting.course_class.code in courses_from_parent1:
                # Shallow copy the meeting, only deep copy when necessary
                new_meeting = State.Allocation(
                    meeting.course_class, meeting.time_slot, meeting.room
                )
                child1.meetings.append(new_meeting)

        for meeting in parent2.meetings:
            if meeting.course_class.code not in courses_from_parent1:
                new_meeting = State.Allocation(
                    meeting.course_class, meeting.time_slot, meeting.room
                )
                child1.meetings.append(new_meeting)

        # Build child2
        for meeting in parent2.meetings:
            if meeting.course_class.code in courses_from_parent1:
                new_meeting = State.Allocation(
                    meeting.course_class, meeting.time_slot, meeting.room
                )
                child2.meetings.append(new_meeting)

        for meeting in parent1.meetings:
            if meeting.course_class.code not in courses_from_parent1:
                new_meeting = State.Allocation(
                    meeting.course_class, meeting.time_slot, meeting.room
                )
                child2.meetings.append(new_meeting)

        return child1, child2

    def mutate(self, individual: State) -> None:
        """
        Mutate an individual in-place to avoid copying.
        """
        if not individual.meetings or not self.is_initialized():
            return

        # Choose mutation type
        mutation_type = random.randint(0, 2)  # 0=time, 1=room, 2=reschedule

        if mutation_type == 0:  # time
            meeting = random.choice(individual.meetings)
            new_day = TimeSlot.Day(random.randint(0, 4))
            max_start = 18 - meeting.time_slot.duration()
            new_start = random.randint(7, max_start)
            new_end = new_start + meeting.time_slot.duration()
            meeting.time_slot = TimeSlot(new_day, new_start, new_end)

        elif mutation_type == 1 and self.room_list:  # room
            meeting = random.choice(individual.meetings)
            meeting.room = random.choice(self.room_list)

        elif mutation_type == 2:  # reschedule
            # Get course codes efficiently
            course_codes = list({m.course_class.code for m in individual.meetings})
            if not course_codes:
                return

            course_to_reschedule = random.choice(course_codes)

            # Remove meetings for this course
            individual.meetings = [
                m
                for m in individual.meetings
                if m.course_class.code != course_to_reschedule
            ]

            # Reschedule the course
            course_class = self.classes[course_to_reschedule]
            hours_to_allocate = course_class.credits

            while hours_to_allocate > 0:
                day = TimeSlot.Day(random.randint(0, 4))
                start_hour = random.randint(7, 17)
                duration = random.randint(1, min(3, hours_to_allocate, 18 - start_hour))
                end_hour = start_hour + duration
                time_slot = TimeSlot(day, start_hour, end_hour)
                room = random.choice(self.room_list)
                meeting = State.Allocation(course_class, time_slot, room)
                individual.meetings.append(meeting)
                hours_to_allocate -= duration

    def get_best_individual_index(self, fitnesses: List[float]) -> int:
        """Get index of best individual efficiently."""
        return max(range(len(fitnesses)), key=lambda i: fitnesses[i])

    def is_initialized(self) -> bool:
        """Check if the algorithm is properly initialized with classes and rooms."""
        return bool(self.classes and self.rooms and self.room_list)

    def optimize(
        self, classes: Dict[str, CourseClass], rooms: Dict[str, Room], show_plot: bool = True
    ) -> Tuple[State, List[float]]:
        """
        Run the genetic algorithm to find optimal schedule.

        Returns:
            Tuple of (best_individual, fitness_history)
        """
        # Clear caches for new optimization
        self._fitness_cache.clear()
        self._penalty_cache.clear()

        # Validate inputs
        if not classes or not rooms:
            raise ValueError("Classes and rooms dictionaries cannot be empty")

        print(
            f"Starting Genetic Algorithm with {self.population_size} individuals for {self.generations} generations..."
        )

        # Initialize population
        population = self.initialize_population(classes, rooms)
        fitness_history = []
        best_penalty_history = []

        # Pre-calculate initial fitnesses
        fitnesses = [self.evaluate_fitness(individual) for individual in population]

        for generation in range(self.generations):
            # Track statistics
            avg_fitness = sum(fitnesses) / len(fitnesses)
            best_fitness_idx = self.get_best_individual_index(fitnesses)
            best_fitness = fitnesses[best_fitness_idx]
            best_penalty = self.get_penalty(population[best_fitness_idx])

            fitness_history.append(avg_fitness)
            best_penalty_history.append(best_penalty)

            if generation % 10 == 0:
                print(
                    f"Generation {generation}: Best Fitness = {best_fitness:.4f}, "
                    f"Best Penalty = {best_penalty:.2f}, Avg Fitness = {avg_fitness:.4f}"
                )

            # Early stopping if we find a perfect solution
            if best_penalty == 0:
                print(f"Perfect solution found at generation {generation}!")
                break

            # Create next generation
            new_population = []
            new_fitnesses = []

            # Keep the best individual (elitism)
            best_individual = copy.deepcopy(population[best_fitness_idx])
            new_population.append(best_individual)
            new_fitnesses.append(fitnesses[best_fitness_idx])

            # Generate offspring
            while len(new_population) < self.population_size:
                # Selection (using indices to avoid copying)
                parent1_idx = self.tournament_selection(population, fitnesses)
                parent2_idx = self.tournament_selection(population, fitnesses)

                # Crossover
                child1, child2 = self.crossover(
                    population[parent1_idx], population[parent2_idx]
                )

                # Mutation (20% chance, in-place)
                if random.random() < 0.2:
                    self.mutate(child1)
                if random.random() < 0.2:
                    self.mutate(child2)

                # Evaluate fitness for new children
                fitness1 = self.evaluate_fitness(child1)
                fitness2 = self.evaluate_fitness(child2)

                new_population.extend([child1, child2])
                new_fitnesses.extend([fitness1, fitness2])

            # Trim to exact population size
            population = new_population[: self.population_size]
            fitnesses = new_fitnesses[: self.population_size]

        # Get final best individual
        best_index = self.get_best_individual_index(fitnesses)
        best_individual = population[best_index]
        final_penalty = self.get_penalty(best_individual)

        print("\nGenetic Algorithm completed!")
        print(f"Best solution penalty: {final_penalty}")
        print(f"Best solution fitness: {fitnesses[best_index]:.4f}")
        print(f"Cache hits: {len(self._fitness_cache)} fitness evaluations cached")

        # Plot the objective value (penalty) progression
        fig = self.plot_objective_progression(best_penalty_history, show=show_plot)

        return best_individual, fitness_history, fig

    def plot_objective_progression(self, penalty_history: List[float], show: bool = True):
        """
        Plot the progression of the objective value (penalty) over generations.

        Args:
            penalty_history: List of best penalty values for each generation
            show: If True, display plot in interactive window
        """
        # Use Figure directly for GUI (thread-safe), plt.figure() for CLI (interactive)
        if show:
            # CLI mode: use plt.figure() for interactive display
            fig, ax = plt.subplots(figsize=(12, 7), facecolor='white')
        else:
            # GUI mode: use Figure directly to avoid threading issues
            from matplotlib.figure import Figure
            fig = Figure(figsize=(12, 7), facecolor='white')
            ax = fig.add_subplot(111)
        
        ax.set_facecolor('white')  # White plot area background
        
        ax.plot(range(len(penalty_history)), penalty_history, "b-", linewidth=2.5)
        ax.set_title(
            "Genetic Algorithm - Objective Value (Penalty) Progression", fontsize=16, fontweight='bold'
        )
        ax.set_xlabel("Generation", fontsize=14, fontweight='bold')
        ax.set_ylabel("Best Penalty Score", fontsize=14, fontweight='bold')
        ax.tick_params(labelsize=11)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()

        # Add some statistics to the plot
        if penalty_history:
            final_penalty = penalty_history[-1]
            initial_penalty = penalty_history[0]
            improvement = initial_penalty - final_penalty

            ax.text(
                0.02,
                0.98,
                f"Initial Penalty: {initial_penalty:.2f}\n"
                f"Final Penalty: {final_penalty:.2f}\n"
                f"Improvement: {improvement:.2f}",
                transform=ax.transAxes,
                fontsize=11,
                verticalalignment="top",
                bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
            )

        if show:
            plt.show()
        
        return fig


def run_genetic_algorithm(
    classes: Dict[str, CourseClass],
    rooms: Dict[str, Room],
    population_size: int = 20,
    generations: int = 100,
) -> State:
    """
    Convenience function to run genetic algorithm with default parameters.

    Args:
        classes: Dictionary of course classes
        rooms: Dictionary of rooms
        population_size: Size of population
        generations: Number of generations

    Returns:
        Best schedule found

    Raises:
        ValueError: If classes or rooms are empty or None
        TypeError: If inputs are not the expected types
    """
    # Input validation
    if not classes or not isinstance(classes, dict):
        raise ValueError("Classes dictionary cannot be empty or None")

    if not rooms or not isinstance(rooms, dict):
        raise ValueError("Rooms dictionary cannot be empty or None")

    if population_size <= 0:
        raise ValueError("Population size must be positive")

    if generations <= 0:
        raise ValueError("Generations must be positive")

    try:
        ga = GeneticAlgorithm(population_size=population_size, generations=generations)

        best_schedule, fitness_history, fig = ga.optimize(classes, rooms, show_plot=True)
        return best_schedule
    except Exception as e:
        raise RuntimeError(f"Genetic algorithm failed: {str(e)}") from e
