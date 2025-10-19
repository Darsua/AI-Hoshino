import copy
import random
import time
from typing import Dict

import matplotlib.pyplot as plt

from src.main.objective import ObjectiveFunction
from src.main.state import State
from src.models import CourseClass, Room
from src.utils.formatter import AlgorithmOutputFormatter


class HillClimbing:
    def __init__(
        self,
        objective_function: ObjectiveFunction,
        rooms: Dict[str, Room],
        classes: Dict[str, CourseClass],
    ):
        self.objective_function = objective_function
        self.rooms = rooms
        self.classes = classes

    def solve(
        self, initial_state: State, variant: str, max_iterations: int = 100, **kwargs
    ):
        start_time = time.time()
        initial_penalty = self.objective_function.calculate(initial_state)

        # Print algorithm start message
        AlgorithmOutputFormatter.print_algorithm_start(
            "Hill Climbing",
            {
                "Variant": variant,
                "Max Iterations": max_iterations,
            },
        )

        # Display initial state
        AlgorithmOutputFormatter.print_initial_state(initial_state, initial_penalty)

        results = {
            "best_state": None,
            "best_penalty": float("inf"),
            "history": [],
            "duration": 0,
            "iterations": 0,
            "restarts": 0,
            "iterations_per_restart": [],
            "variant": variant,
            "initial_penalty": initial_penalty,
        }

        if variant == "stochastic":
            best_state, history = self._stochastic_hc(initial_state, max_iterations)
            results["iterations"] = len(history)
            results["history"] = history
        elif variant == "steepest_ascent":
            best_state, history = self._steepest_ascent_hc(
                initial_state, max_iterations
            )
            results["iterations"] = len(history)
            results["history"] = history
        elif variant == "sideways_move":
            max_sideways_moves = kwargs.get("max_sideways_moves", 100)
            best_state, history, sideways_moves_taken = self._sideways_move_hc(
                initial_state, max_iterations, max_sideways_moves
            )
            results["iterations"] = len(history)
            results["sideways_moves_taken"] = sideways_moves_taken
            results["history"] = history
        elif variant == "random_restart":
            max_restarts = kwargs.pop("max_restarts", 10)
            restart_variant = kwargs.pop("restart_variant", "steepest_ascent")
            best_state, history, iterations_per_restart = self._random_restart_hc(
                max_iterations, max_restarts, restart_variant, **kwargs
            )
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
        results["variant"] = variant

        # Print completion summary
        AlgorithmOutputFormatter.print_algorithm_completion(
            "Hill Climbing", results, initial_penalty, duration
        )

        return best_state, results

    def plot_results(self, results: Dict, show: bool = True):
        """
        Plot optimization results. Set show=False when using with GUI to prevent popup windows.
        """
        variant = results.get("variant", "Hill Climbing")
        title = f"{variant.replace('_', ' ').title()} Optimization"
        history = results.get("history", [])

        xlabel = "Iterations"

        # Use Figure directly for GUI (thread-safe), plt.figure() for CLI (interactive)
        if show:
            # CLI mode: use plt.figure() for interactive display
            fig, ax = plt.subplots(figsize=(12, 6), facecolor="white")
        else:
            # GUI mode: use Figure directly to avoid threading issues
            from matplotlib.figure import Figure

            fig = Figure(figsize=(12, 6), facecolor="white")
            ax = fig.add_subplot(111)

        ax.set_facecolor("white")  # White plot area background
        ax.plot(
            range(len(history)),
            history,
            marker="o",
            linewidth=2,
            markersize=5,
            color="tab:blue",
            alpha=0.8,
        )
        ax.set_title(title, fontsize=16, fontweight="bold")
        ax.set_xlabel(xlabel, fontsize=14, fontweight="bold")
        ax.set_ylabel("Penalty", fontsize=14, fontweight="bold")
        ax.tick_params(labelsize=11)
        ax.grid(True, alpha=0.3)

        fig.tight_layout()

        if show:
            plt.show()

        return fig

    def _stochastic_hc(self, initial_state: State, max_iterations: int):
        current_state = initial_state
        current_value = self.objective_function.calculate(current_state)
        best_state = current_state
        best_value = current_value

        history = [current_value]

        for i in range(max_iterations):
            neighbor = current_state.get_random_neighbor(self.rooms)
            if neighbor is None:
                # No valid neighbor could be generated, continue to next iteration
                history.append(best_value)
                continue

            # Evaluate the neighbor
            neighbor_value = self.objective_function.calculate(neighbor)

            # Move to neighbor only if it's better (uphill move)
            if neighbor_value < current_value:
                current_state = neighbor
                current_value = neighbor_value

                # Update best if this is the best so far
                if current_value < best_value:
                    best_state = copy.deepcopy(current_state)
                    best_value = current_value
                    # Print progress on improvement
                    AlgorithmOutputFormatter.print_progress(
                        i + 1, best_value, "Improvement found!"
                    )

                    # Check for perfect solution
                    if best_value == 0:
                        AlgorithmOutputFormatter.print_perfect_solution(
                            i + 1, "iteration"
                        )
                        break

            history.append(best_value)

        return best_state, history

    def _steepest_ascent_hc(self, initial_state: State, max_iterations: int):
        current_state = initial_state
        current_value = self.objective_function.calculate(current_state)
        best_state = copy.deepcopy(current_state)
        best_value = current_value
        history = [current_value]

        for i in range(max_iterations):
            neighbors = current_state.get_all_neighbors(self.rooms)
            best_neighbor = None
            best_neighbor_value = float("inf")

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
                    # Print progress on improvement
                    AlgorithmOutputFormatter.print_progress(
                        i + 1, best_value, "Improvement found!"
                    )

                    # Check for perfect solution
                    if best_value == 0:
                        AlgorithmOutputFormatter.print_perfect_solution(
                            i + 1, "iteration"
                        )
                        break
            else:
                # No better neighbor found, reached local optimum
                # Print final progress before breaking
                AlgorithmOutputFormatter.print_progress(
                    i + 1, best_value, "Local optimum reached"
                )
                break

            history.append(best_value)

        return best_state, history

    def _sideways_move_hc(
        self, initial_state: State, max_iterations: int, max_sideways_moves: int
    ):
        current_state = initial_state
        current_value = self.objective_function.calculate(current_state)
        best_state = current_state
        best_value = current_value
        sideways_moves = 0
        stagnation_count = 0

        history = [current_value]

        for i in range(max_iterations):
            neighbors = current_state.get_all_neighbors(self.rooms)
            if not neighbors:
                break

            best_neighbors = []
            best_neighbor_value = float("inf")
            for neighbor in neighbors:
                value = self.objective_function.calculate(neighbor)
                if value < best_neighbor_value:
                    best_neighbor_value = value
                    best_neighbors = [neighbor]
                elif value == best_neighbor_value:
                    best_neighbors.append(neighbor)

            chosen = random.choice(best_neighbors) if best_neighbors else None
            if chosen is None:
                break

            if best_neighbor_value < current_value:
                current_state = chosen
                current_value = best_neighbor_value
                sideways_moves = 0
                stagnation_count = 0
            elif (
                best_neighbor_value == current_value
                and sideways_moves < max_sideways_moves
            ):
                current_state = chosen
                sideways_moves += 1
                stagnation_count = 0
                # Print progress on sideways move
                AlgorithmOutputFormatter.print_progress(
                    i + 1,
                    best_value,
                    f"Sideways move {sideways_moves}/{max_sideways_moves}",
                )
            else:
                stagnation_count += 1

            if current_value < best_value:
                best_state = copy.deepcopy(current_state)
                best_value = current_value
                sideways_moves = 0  # Reset on new best
                # Print progress on improvement
                AlgorithmOutputFormatter.print_progress(
                    i + 1, best_value, "Improvement found!"
                )

                # Check for perfect solution
                if best_value == 0:
                    AlgorithmOutputFormatter.print_perfect_solution(i + 1, "iteration")
                    break

            history.append(best_value)

            if sideways_moves >= max_sideways_moves:
                AlgorithmOutputFormatter.print_progress(
                    i + 1,
                    best_value,
                    f"Max sideways moves ({max_sideways_moves}) reached",
                )
                break
            if stagnation_count > 100:  # Also stop if truly stuck
                break

        return best_state, history, sideways_moves

    def _random_restart_hc(
        self, max_iterations: int, max_restarts: int, restart_variant: str, **kwargs
    ):
        best_state_overall = None
        best_value_overall = float("inf")
        best_history_so_far = []  # Will store the history of the best run
        iterations_per_restart = []

        for i in range(max_restarts):
            # Print restart progress
            AlgorithmOutputFormatter.print_restart_progress(i + 1, max_restarts)

            initial_state = State()
            initial_state.random_fill(self.classes, self.rooms)

            if restart_variant == "stochastic":
                best_state, history = self._stochastic_hc(initial_state, max_iterations)
            elif restart_variant == "steepest_ascent":
                best_state, history = self._steepest_ascent_hc(
                    initial_state, max_iterations
                )
            elif restart_variant == "sideways_move":
                max_sideways_moves = kwargs.get("max_sideways_moves", 100)
                best_state, history, _ = self._sideways_move_hc(
                    initial_state, max_iterations, max_sideways_moves
                )
            else:  # Default to stochastic
                best_state, history = self._stochastic_hc(initial_state, max_iterations)

            iterations_per_restart.append(len(history))
            current_best_value = self.objective_function.calculate(best_state)

            if current_best_value < best_value_overall:
                best_state_overall = copy.deepcopy(best_state)
                best_value_overall = current_best_value
                best_history_so_far = history  # Save the history of the best run
                # Print progress on overall improvement
                AlgorithmOutputFormatter.print_progress(
                    i + 1, best_value_overall, f"New best from restart {i + 1}!"
                )

                # Check for perfect solution
                if best_value_overall == 0:
                    AlgorithmOutputFormatter.print_perfect_solution(i + 1, "restart")
                    break

        return best_state_overall, best_history_so_far, iterations_per_restart
