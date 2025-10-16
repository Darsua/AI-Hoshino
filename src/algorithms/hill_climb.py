from src.main.state import State
from src.main.objective import ObjectiveFunction
from src.models import Room, CourseClass
from src.utils.plotter import plot_results as plot
import time
import copy

class HillClimbing:
    def __init__(self, objective_function: ObjectiveFunction, rooms: dict[str, Room], classes: dict[str, CourseClass]):
        self.objective_function = objective_function
        self.rooms = rooms
        self.classes = classes

    def solve(self, initial_state: State, variant: str, max_iterations: int = 1000, **kwargs):
        start_time = time.time()
        
        results = {
            "best_state": None,
            "best_penalty": float('inf'),
            "history": [],
            "duration": 0,
            "iterations": 0,
            "restarts": 0,
            "iterations_per_restart": [],
            "variant": variant
        }

        if variant == 'stochastic':
            best_state, history = self._stochastic_hc(initial_state, max_iterations)
            results["iterations"] = len(history)
            results["history"] = history
        elif variant == 'steepest_ascent':
            num_neighbors = kwargs.get('num_neighbors', 10)
            best_state, history = self._steepest_ascent_hc(initial_state, max_iterations, num_neighbors)
            results["iterations"] = len(history)
            results["history"] = history
        elif variant == 'sideways_move':
            max_sideways_moves = kwargs.get('max_sideways_moves', 100)
            best_state, history, sideways_moves_taken = self._sideways_move_hc(initial_state, max_iterations, max_sideways_moves)
            results["iterations"] = len(history)
            results["sideways_moves_taken"] = sideways_moves_taken
            results["history"] = history
        elif variant == 'random_restart':
            max_restarts = kwargs.get('max_restarts', 10)
            restart_variant = kwargs.get('restart_variant', 'steepest_ascent')
            best_state, history, iterations_per_restart = self._random_restart_hc(max_iterations, max_restarts, restart_variant, **kwargs)
            results["iterations"] = sum(iterations_per_restart)
            results["restarts"] = len(iterations_per_restart)
            results["iterations_per_restart"] = iterations_per_restart
            # For random restart, history tracks the best penalty of each restart
            results["history"] = history 
        else:
            raise ValueError(f"Unknown Hill Climbing variant: {variant}")

        duration = time.time() - start_time
        
        results["best_state"] = best_state
        results["best_penalty"] = self.objective_function.calculate(best_state)
        results["duration"] = duration
        
        return best_state, results

    def plot_results(self, results: dict):
        variant = results.get("variant", "Hill Climbing")
        title = f'{variant.replace("_", " ").title()} Optimization'
        history = results["history"]
        
        # For random_restart, the history is of best values per restart, so x-axis is restarts
        xlabel = "Restarts" if variant == "random_restart" else "Iterations"
        
        plot(history, title, xlabel)

    def _stochastic_hc(self, initial_state: State, max_iterations: int):
        current_state = initial_state
        current_value = self.objective_function.calculate(current_state)
        best_state = current_state
        best_value = current_value
        
        history = [current_value]
        stagnation_count = 0

        for i in range(max_iterations):
            neighbor = current_state.get_random_neighbor(self.rooms)
            neighbor_value = self.objective_function.calculate(neighbor)

            if neighbor_value < current_value:
                current_state = neighbor
                current_value = neighbor_value
                stagnation_count = 0
            else:
                stagnation_count += 1

            if current_value < best_value:
                best_state = copy.deepcopy(current_state)
                best_value = current_value
            
            history.append(best_value)
            if stagnation_count >= 100: # Stop if no improvement for 100 iterations
                break

        return best_state, history

    def _steepest_ascent_hc(self, initial_state: State, max_iterations: int, num_neighbors: int):
        current_state = initial_state
        current_value = self.objective_function.calculate(current_state)
        best_state = copy.deepcopy(current_state)
        best_value = current_value
        history = [current_value]

        for i in range(max_iterations):
            neighbors = current_state.get_N_random_neighbors(num_neighbors, self.rooms)
            best_neighbor = None
            best_neighbor_value = float('inf')
            
            for neighbor in neighbors:
                neighbor_value = self.objective_function.calculate(neighbor)
                if neighbor_value < best_neighbor_value:
                    best_neighbor = neighbor
                    best_neighbor_value = neighbor_value

            if best_neighbor_value < current_value:
                current_state = best_neighbor
                current_value = best_neighbor_value
                
                if current_value < best_value:
                    best_state = copy.deepcopy(current_state)
                    best_value = current_value
            else:
                # No better neighbor found, reached local optimum
                break
                
            history.append(best_value)

        return best_state, history

    def _sideways_move_hc(self, initial_state: State, max_iterations: int, max_sideways_moves: int):
        current_state = initial_state
        current_value = self.objective_function.calculate(current_state)
        best_state = current_state
        best_value = current_value
        sideways_moves = 0
        stagnation_count = 0

        history = [current_value]

        for i in range(max_iterations):
            neighbor = current_state.get_random_neighbor(self.rooms)
            neighbor_value = self.objective_function.calculate(neighbor)

            if neighbor_value < current_value:
                current_state = neighbor
                current_value = neighbor_value
                sideways_moves = 0
                stagnation_count = 0
            elif neighbor_value == current_value and sideways_moves < max_sideways_moves:
                current_state = neighbor
                sideways_moves += 1
                stagnation_count = 0
            else:
                stagnation_count += 1

            if current_value < best_value:
                best_state = copy.deepcopy(current_state)
                best_value = current_value
                sideways_moves = 0 # Reset on new best

            history.append(best_value)
            
            if sideways_moves >= max_sideways_moves:
                break
            if stagnation_count > 100: # Also stop if truly stuck
                break

        return best_state, history, sideways_moves

    def _random_restart_hc(self, max_iterations: int, max_restarts: int, restart_variant: str, **kwargs):
        best_state_overall = None
        best_value_overall = float('inf')
        history_overall = []
        iterations_per_restart = []

        for i in range(max_restarts):
            # print(f"Restart {i+1}/{max_restarts}...")
            initial_state = State()
            initial_state.random_fill(self.classes, self.rooms)
            
            if restart_variant == 'stochastic':
                best_state, history = self._stochastic_hc(initial_state, max_iterations)
            elif restart_variant == 'steepest_ascent':
                num_neighbors = kwargs.get('num_neighbors', 10)
                best_state, history = self._steepest_ascent_hc(initial_state, max_iterations, num_neighbors)
            elif restart_variant == 'sideways_move':
                max_sideways_moves = kwargs.get('max_sideways_moves', 100)
                best_state, history, _ = self._sideways_move_hc(initial_state, max_iterations, max_sideways_moves)
            else: # Default to stochastic
                best_state, history = self._stochastic_hc(initial_state, max_iterations)

            iterations_per_restart.append(len(history))
            current_best_value = self.objective_function.calculate(best_state)

            if current_best_value < best_value_overall:
                best_state_overall = copy.deepcopy(best_state)
                best_value_overall = current_best_value
            
            history_overall.append(current_best_value) # Track best of each restart

        return best_state_overall, history_overall, iterations_per_restart
