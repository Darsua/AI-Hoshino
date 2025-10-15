import random
import copy
from typing import List, Dict, Tuple
from src.main.state import State
from src.main.objective import ObjectiveFunction
from src.models import TimeSlot, CourseClass, Room


class GeneticAlgorithm:
    def __init__(self,
                 population_size: int = 20,
                 generations: int = 100):
        """
        Initialize the Genetic Algorithm for course scheduling.

        Args:
            population_size: Number of individuals in each generation
            generations: Number of generations to evolve
        """
        self.population_size = population_size
        self.generations = generations
        self.objective_function = ObjectiveFunction()

        # Will be set during optimization
        self.classes: Dict[str, CourseClass] = {}
        self.rooms: Dict[str, Room] = {}
        self.room_list: List[Room] = []

    def initialize_population(self, classes: Dict[str, CourseClass], rooms: Dict[str, Room]) -> List[State]:
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
        Evaluate fitness of an individual (lower penalty = higher fitness).
        Since objective function returns penalty, we use 1/(1+penalty) for fitness.
        """
        penalty = self.objective_function.calculate(individual)
        # Convert penalty to fitness (higher fitness is better)
        fitness = 1.0 / (1.0 + penalty)
        return fitness

    def tournament_selection(self, population: List[State], fitnesses: List[float]) -> State:
        """Select an individual using tournament selection with size 2."""
        tournament_indices = random.sample(range(len(population)), 2)
        best_index = max(tournament_indices, key=lambda i: fitnesses[i])
        return population[best_index]

    def crossover(self, parent1: State, parent2: State) -> Tuple[State, State]:
        """
        Perform crossover between two parents to create two offspring.
        Uses order-based crossover where we swap allocations for random courses.
        """
        child1 = State()
        child2 = State()

        # Get all unique course codes from both parents
        all_courses = set()
        for meeting in parent1.meetings + parent2.meetings:
            all_courses.add(meeting.course_class.code)

        # Randomly decide which courses come from which parent
        courses_from_parent1 = set(random.sample(list(all_courses),
                                                len(all_courses) // 2))

        # Build child1: courses in set from parent1, others from parent2
        for meeting in parent1.meetings:
            if meeting.course_class.code in courses_from_parent1:
                child1.meetings.append(copy.deepcopy(meeting))

        for meeting in parent2.meetings:
            if meeting.course_class.code not in courses_from_parent1:
                child1.meetings.append(copy.deepcopy(meeting))

        # Build child2: opposite assignment
        for meeting in parent2.meetings:
            if meeting.course_class.code in courses_from_parent1:
                child2.meetings.append(copy.deepcopy(meeting))

        for meeting in parent1.meetings:
            if meeting.course_class.code not in courses_from_parent1:
                child2.meetings.append(copy.deepcopy(meeting))

        return child1, child2

    def mutate(self, individual: State) -> State:
        """
        Mutate an individual by randomly changing some allocations.
        """
        mutated = copy.deepcopy(individual)

        if not mutated.meetings:
            return mutated

        # Safety check: ensure algorithm is properly initialized
        if not self.is_initialized():
            return mutated

        # Choose mutation type randomly
        mutation_type = random.choice(['time', 'room', 'reschedule'])

        if mutation_type == 'time':
            # Change time slot of a random meeting
            meeting = random.choice(mutated.meetings)
            new_day = TimeSlot.Day(random.randint(0, 4))
            max_start = 18 - meeting.time_slot.duration()
            new_start = random.randint(7, max_start)
            new_end = new_start + meeting.time_slot.duration()
            meeting.time_slot = TimeSlot(new_day, new_start, new_end)

        elif mutation_type == 'room':
            # Change room of a random meeting
            if self.room_list:
                meeting = random.choice(mutated.meetings)
                meeting.room = random.choice(self.room_list)

        elif mutation_type == 'reschedule':
            # Completely reschedule a random course
            if mutated.meetings and self.classes and self.room_list:
                # Remove all meetings for a random course
                course_codes = list(set(m.course_class.code for m in mutated.meetings))
                if course_codes:
                    course_to_reschedule = random.choice(course_codes)
                    mutated.meetings = [m for m in mutated.meetings
                                      if m.course_class.code != course_to_reschedule]

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
                        mutated.meetings.append(meeting)
                        hours_to_allocate -= duration

        return mutated

    def get_best_individual(self, population: List[State], fitnesses: List[float]) -> State:
        """Get the best individual from the population."""
        best_index = fitnesses.index(max(fitnesses))
        return copy.deepcopy(population[best_index])

    def is_initialized(self) -> bool:
        """Check if the algorithm is properly initialized with classes and rooms."""
        return bool(self.classes and self.rooms and self.room_list)

    def optimize(self, classes: Dict[str, CourseClass], rooms: Dict[str, Room]) -> Tuple[State, List[float]]:
        """
        Run the genetic algorithm to find optimal schedule.

        Returns:
            Tuple of (best_individual, fitness_history)
        """
        # Validate inputs
        if not classes or not rooms:
            raise ValueError("Classes and rooms dictionaries cannot be empty")

        print(f"Starting Genetic Algorithm with {self.population_size} individuals for {self.generations} generations...")

        # Initialize population
        population = self.initialize_population(classes, rooms)
        fitness_history = []
        best_fitness_history = []

        for generation in range(self.generations):
            # Evaluate fitness
            fitnesses = [self.evaluate_fitness(individual) for individual in population]

            # Track statistics
            avg_fitness = sum(fitnesses) / len(fitnesses)
            best_fitness = max(fitnesses)
            best_penalty = self.objective_function.calculate(population[fitnesses.index(best_fitness)])

            fitness_history.append(avg_fitness)
            best_fitness_history.append(best_fitness)

            if generation % 10 == 0:
                print(f"Generation {generation}: Best Fitness = {best_fitness:.4f}, "
                      f"Best Penalty = {best_penalty:.2f}, Avg Fitness = {avg_fitness:.4f}")

            # Early stopping if we find a perfect solution
            if best_penalty == 0:
                print(f"Perfect solution found at generation {generation}!")
                break

            # Create next generation
            new_population = []

            # Keep the best individual
            best_individual = self.get_best_individual(population, fitnesses)
            new_population.append(best_individual)

            # Generate offspring through crossover and mutation
            while len(new_population) < self.population_size:
                # Selection
                parent1 = self.tournament_selection(population, fitnesses)
                parent2 = self.tournament_selection(population, fitnesses)

                # Crossover
                child1, child2 = self.crossover(parent1, parent2)

                # Mutation (20% chance)
                if random.random() < 0.2:
                    child1 = self.mutate(child1)
                if random.random() < 0.2:
                    child2 = self.mutate(child2)

                new_population.extend([child1, child2])

            # Trim to exact population size
            population = new_population[:self.population_size]

        # Return best individual
        final_fitnesses = [self.evaluate_fitness(individual) for individual in population]
        best_index = final_fitnesses.index(max(final_fitnesses))
        best_individual = population[best_index]
        final_penalty = self.objective_function.calculate(best_individual)

        print("\nGenetic Algorithm completed!")
        print(f"Best solution penalty: {final_penalty}")
        print(f"Best solution fitness: {max(final_fitnesses):.4f}")

        return best_individual, fitness_history


def run_genetic_algorithm(classes: Dict[str, CourseClass],
                         rooms: Dict[str, Room],
                         population_size: int = 20,
                         generations: int = 100) -> State:
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
        ga = GeneticAlgorithm(
            population_size=population_size,
            generations=generations
        )

        best_schedule, fitness_history = ga.optimize(classes, rooms)
        return best_schedule
    except Exception as e:
        raise RuntimeError(f"Genetic algorithm failed: {str(e)}") from e
