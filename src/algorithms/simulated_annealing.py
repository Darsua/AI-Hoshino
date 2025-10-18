import copy
import math
import random
import time
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt

from src.main.objective import ObjectiveFunction
from src.main.state import State
from src.models import CourseClass, Room, TimeSlot
from src.utils.formatter import AlgorithmOutputFormatter, ProgressTracker


class SimulatedAnnealing:
    def __init__(
        self,
        classes: Dict[str, CourseClass],
        rooms: Dict[str, Room],
        objective_function: ObjectiveFunction,
        initial_temp: float = 500.0,
        cooling_rate: float = 0.97,
        min_temp: float = 0.01,
        max_iterations: int = 5000,
    ):
        self.classes = classes
        self.rooms = rooms
        self.objective_function = objective_function
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.min_temp = min_temp
        self.max_iterations = max_iterations

        # Tracking variables
        self.objective_history = []
        self.acceptance_prob_history = []
        self.temperature_history = []
        self.best_objective_history = []
        self.local_optima_count = 0
        self.iterations_stuck = []

    def acceptance_probability(
        self, current_penalty: float, neighbor_penalty: float, temperature: float
    ) -> float:
        # If neighbor is better, always accept
        if neighbor_penalty < current_penalty:
            return 1.0

        # If neighbor is worse, accept with probability e^(ΔE/T)
        # ΔE = current_penalty - neighbor_penalty (negative since neighbor is worse)
        delta_E = current_penalty - neighbor_penalty

        # Avoid division by zero or overflow
        if temperature < 1e-10:
            return 0.0

        try:
            probability = math.exp(delta_E / temperature)
        except OverflowError:
            probability = 1.0

        return min(probability, 1.0)

    def detect_local_optimum(self, window_size: int = 50) -> bool:
        if len(self.best_objective_history) < window_size:
            return False

        recent_bests = self.best_objective_history[-window_size:]
        # Check if all recent values are the same (or very close)
        if max(recent_bests) - min(recent_bests) < 0.01:
            return True

        return False

    def run(self, verbose: bool = True) -> Tuple[State, Dict]:
        start_time = time.time()

        # Initialize random state
        current_state = State()
        current_state.random_fill(self.classes, self.rooms)
        initial_state = copy.deepcopy(current_state)

        # Calculate initial penalty
        current_penalty = self.objective_function.calculate(current_state)
        initial_penalty = current_penalty

        # Track best solution
        best_state = copy.deepcopy(current_state)
        best_penalty = current_penalty

        # Initialize temperature
        temperature = self.initial_temp

        # Reset tracking
        self.objective_history = [current_penalty]
        self.acceptance_prob_history = []
        self.temperature_history = [temperature]
        self.best_objective_history = [best_penalty]
        self.local_optima_count = 0
        self.iterations_stuck = []

        iteration = 0
        last_stuck_check = 0

        if verbose:
            # Print algorithm start message
            AlgorithmOutputFormatter.print_algorithm_start(
                "Simulated Annealing",
                {
                    "Initial Temperature": f"{temperature:.2f}",
                    "Cooling Rate": self.cooling_rate,
                    "Max Iterations": self.max_iterations,
                },
            )

            # Display initial state
            AlgorithmOutputFormatter.print_initial_state(current_state, initial_penalty)

            # Check if initial state is already perfect
            if initial_penalty == 0:
                AlgorithmOutputFormatter.print_perfect_solution(0, "iteration")
                end_time = time.time()
                duration = end_time - start_time

                results_dict = {
                    "iterations": 0,
                    "best_penalty": initial_penalty,
                    "duration": duration,
                    "local_optima_count": 0,
                }
                AlgorithmOutputFormatter.print_algorithm_completion(
                    "Simulated Annealing", results_dict, initial_penalty, duration
                )

                results = {
                    "initial_state": initial_state,
                    "final_state": current_state,
                    "best_state": best_state,
                    "initial_penalty": initial_penalty,
                    "final_penalty": current_penalty,
                    "best_penalty": best_penalty,
                    "iterations": 0,
                    "duration": duration,
                    "objective_history": self.objective_history,
                    "acceptance_prob_history": self.acceptance_prob_history,
                    "temperature_history": self.temperature_history,
                    "best_objective_history": self.best_objective_history,
                    "local_optima_count": self.local_optima_count,
                    "iterations_stuck": self.iterations_stuck,
                }
                return best_state, results

        # Main loop
        while temperature > self.min_temp and iteration < self.max_iterations:
            # Generate neighbor
            neighbor_state = current_state.get_random_neighbor(self.rooms)
            neighbor_penalty = self.objective_function.calculate(neighbor_state)

            # Calculate acceptance probability
            accept_prob = self.acceptance_probability(
                current_penalty, neighbor_penalty, temperature
            )
            self.acceptance_prob_history.append(accept_prob)

            # Decide whether to accept neighbor
            if random.random() < accept_prob:
                current_state = neighbor_state
                current_penalty = neighbor_penalty

                # Update best solution if improved
                if current_penalty < best_penalty:
                    best_state = copy.deepcopy(current_state)
                    best_penalty = current_penalty

                    # Check for perfect solution
                    if best_penalty == 0:
                        if verbose:
                            AlgorithmOutputFormatter.print_perfect_solution(
                                iteration + 1, "iteration"
                            )
                        break

            # Record history
            self.objective_history.append(current_penalty)
            self.best_objective_history.append(best_penalty)

            # Cool down temperature
            temperature *= self.cooling_rate
            self.temperature_history.append(temperature)

            # Check for local optima periodically (every 50 iterations)
            if iteration - last_stuck_check >= 50:
                if self.detect_local_optimum():
                    self.local_optima_count += 1
                    self.iterations_stuck.append(iteration)
                last_stuck_check = iteration

            # Print progress - adaptive frequency for SA to show progress even with early termination
            # Use smaller intervals or every 50 iterations, whichever is smaller
            progress_interval = min(50, max(1, self.max_iterations // 50))
            if verbose and (iteration + 1) % progress_interval == 0:
                AlgorithmOutputFormatter.print_progress(
                    iteration + 1,
                    best_penalty,
                    f"Temperature = {temperature:.4f}",
                )

            iteration += 1

        end_time = time.time()
        duration = end_time - start_time

        if verbose:
            # Print completion summary
            results_dict = {
                "iterations": iteration,
                "best_penalty": best_penalty,
                "duration": duration,
                "local_optima_count": self.local_optima_count,
            }
            AlgorithmOutputFormatter.print_algorithm_completion(
                "Simulated Annealing", results_dict, initial_penalty, duration
            )

        results = {
            "initial_state": initial_state,
            "final_state": current_state,
            "best_state": best_state,
            "initial_penalty": initial_penalty,
            "final_penalty": current_penalty,
            "best_penalty": best_penalty,
            "iterations": iteration,
            "duration": duration,
            "objective_history": self.objective_history,
            "acceptance_prob_history": self.acceptance_prob_history,
            "temperature_history": self.temperature_history,
            "best_objective_history": self.best_objective_history,
            "local_optima_count": self.local_optima_count,
            "iterations_stuck": self.iterations_stuck,
        }

        return best_state, results

    def plot_results(self, results: Dict, save_path: str = None, show: bool = True):
        """
        Plot optimization results. Set show=False when using with GUI to prevent popup windows.
        """
        figures = []

        # ========== PLOT 1: Objective Function vs Iterations ==========
        # Use Figure directly for GUI (thread-safe), plt.figure() for CLI (interactive)
        if show:
            # CLI mode: use plt.figure() for interactive display
            fig1 = plt.figure(figsize=(14, 7), facecolor="white")
            ax1 = fig1.add_axes([0.08, 0.12, 0.65, 0.78])
        else:
            # GUI mode: use Figure directly to avoid threading issues
            from matplotlib.figure import Figure

            fig1 = Figure(figsize=(14, 7), facecolor="white")
            ax1 = fig1.add_axes([0.08, 0.12, 0.65, 0.78])

        ax1.set_facecolor("white")  # White plot area background

        iterations = range(len(results["objective_history"]))

        # Plot current and best penalty
        ax1.plot(
            iterations,
            results["objective_history"],
            label="Current Penalty",
            alpha=0.7,
            linewidth=1.5,
            color="#3B82F6",
        )
        ax1.plot(
            iterations,
            results["best_objective_history"],
            label="Best Penalty Found",
            linewidth=2.5,
            color="#10B981",
        )

        # Mark local optima points if any
        if results["iterations_stuck"]:
            stuck_iterations = results["iterations_stuck"]
            stuck_penalties = [
                results["objective_history"][i]
                for i in stuck_iterations
                if i < len(results["objective_history"])
            ]
            ax1.scatter(
                stuck_iterations[: len(stuck_penalties)],
                stuck_penalties,
                color="#EF4444",
                s=120,
                marker="x",
                linewidth=3,
                label=f"Stuck in Local Optima ({results['local_optima_count']}x)",
                zorder=5,
            )

        ax1.set_xlabel("Iteration", fontsize=7, fontweight="bold")
        ax1.set_ylabel(
            "Penalty (Objective Function Value)", fontsize=7, fontweight="bold"
        )
        ax1.set_title(
            "Simulated Annealing: Objective Function vs Iterations",
            fontsize=8,
            fontweight="bold",
            pad=15,
        )
        ax1.legend(loc="upper right", fontsize=5.5, framealpha=0.9)
        ax1.grid(True, alpha=0.3, linestyle="--")
        ax1.tick_params(labelsize=5.5)

        # Add summary text box outside plot area (top right)
        # Make it more compact for GUI display
        summary_text = "SUMMARY\n" + "=" * 22 + "\n"
        summary_text += f"Initial:    {results['initial_penalty']:.2f}\n"
        summary_text += f"Final:      {results['final_penalty']:.2f}\n"
        summary_text += f"Best:       {results['best_penalty']:.2f}\n"
        improvement = results["initial_penalty"] - results["best_penalty"]
        improvement_pct = (
            (improvement / results["initial_penalty"] * 100)
            if results["initial_penalty"] > 0
            else 0
        )
        summary_text += f"Improve:    {improvement:.2f} ({improvement_pct:.1f}%)\n"
        summary_text += f"Iterations: {results['iterations']}\n"
        summary_text += f"Duration:   {results['duration']:.2f}s\n"
        summary_text += f"Local Opt:  {results['local_optima_count']}"

        fig1.text(
            0.77,
            0.88,
            summary_text,
            transform=fig1.transFigure,
            fontsize=9,
            verticalalignment="top",
            family="monospace",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.9, pad=1),
        )

        figures.append(fig1)

        # ========== PLOT 2: Acceptance Probability vs Iterations ==========
        # Use Figure directly for GUI (thread-safe), plt.figure() for CLI (interactive)
        if show:
            # CLI mode: use plt.figure() for interactive display
            fig2 = plt.figure(figsize=(14, 7), facecolor="white")
            ax2 = fig2.add_axes([0.08, 0.12, 0.65, 0.78])
        else:
            # GUI mode: use Figure directly to avoid threading issues
            from matplotlib.figure import Figure

            fig2 = Figure(figsize=(14, 7), facecolor="white")
            ax2 = fig2.add_axes([0.08, 0.12, 0.65, 0.78])

        ax2.set_facecolor("white")  # White plot area background

        acceptance_iterations = range(len(results["acceptance_prob_history"]))

        # Plot acceptance probability
        ax2.plot(
            acceptance_iterations,
            results["acceptance_prob_history"],
            color="#F59E0B",
            alpha=0.7,
            linewidth=1.5,
            label="Acceptance Probability",
        )

        # Add average line
        avg_accept = sum(results["acceptance_prob_history"]) / len(
            results["acceptance_prob_history"]
        )
        ax2.axhline(
            y=avg_accept,
            color="#EF4444",
            linestyle="--",
            linewidth=2,
            label=f"Average: {avg_accept:.3f}",
        )

        # Add threshold reference line (removed text label from plot)
        ax2.axhline(
            y=0.5,
            color="#6B7280",
            linestyle=":",
            linewidth=1,
            alpha=0.5,
            label="50% threshold",
        )

        ax2.set_xlabel("Iteration", fontsize=7, fontweight="bold")
        ax2.set_ylabel("Acceptance Probability e^(ΔE/T)", fontsize=7, fontweight="bold")
        ax2.set_title(
            "Simulated Annealing: Acceptance Probability vs Iterations",
            fontsize=8,
            fontweight="bold",
            pad=15,
        )
        ax2.set_ylim(-0.05, 1.05)
        ax2.legend(loc="upper right", fontsize=5.5, framealpha=0.9)
        ax2.grid(True, alpha=0.3, linestyle="--")
        ax2.tick_params(labelsize=5.5)

        # Add info text box outside plot area (top right)
        high_accept_rate = (
            len([p for p in results["acceptance_prob_history"] if p > 0.5])
            / len(results["acceptance_prob_history"])
            * 100
        )
        info_text = "PARAMETERS\n" + "=" * 20 + "\n"
        info_text += f"Init Temp:  {self.initial_temp:.1f}\n"
        info_text += f"Final Temp: {results['temperature_history'][-1]:.4f}\n"
        info_text += f"Cool Rate:  {self.cooling_rate}\n"
        info_text += "\nSTATISTICS\n" + "=" * 20 + "\n"
        info_text += f"Avg Accept: {avg_accept:.3f}\n"
        info_text += f"High Rate:  {high_accept_rate:.1f}%\n"
        info_text += f"(>50% thr.)"

        fig2.text(
            0.77,
            0.88,
            info_text,
            transform=fig2.transFigure,
            fontsize=9,
            verticalalignment="top",
            family="monospace",
            bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.9, pad=1),
        )

        figures.append(fig2)

        # Display all figures only if show=True (CLI mode)
        if show:
            plt.show()

        return figures
