"""
Centralized output formatting utility for AI-Hoshino algorithms.

This module provides standardized formatting functions to eliminate duplicate
print statements across different optimization algorithms.
"""

from typing import Dict, Any, Optional
from src.main.state import State


class AlgorithmOutputFormatter:
    """Centralized formatter for algorithm output with consistent styling."""

    SEPARATOR_LENGTH = 70
    SEPARATOR = "-" * SEPARATOR_LENGTH

    @classmethod
    def print_algorithm_start(
        cls, algorithm_name: str, parameters: Dict[str, Any]
    ) -> None:
        """Print standardized algorithm start message with parameters."""
        print(f"Starting {algorithm_name}...")
        for param_name, param_value in parameters.items():
            print(f"{param_name}: {param_value}")
        print(cls.SEPARATOR)

    @classmethod
    def print_initial_state(
        cls, state: State, penalty: float, title: str = "Initial State"
    ) -> None:
        """Print standardized initial state display."""
        print(f"{title}:")
        print(state)
        print(f"Initial Penalty: {penalty:.2f}")
        print(cls.SEPARATOR)

    @classmethod
    def print_progress(
        cls,
        iteration: int,
        best_penalty: float,
        extra_info: Optional[str] = None,
    ) -> None:
        """Print standardized progress update."""
        base_msg = f"Iteration {iteration:4d}, Best Penalty = {best_penalty:.2f}"
        if extra_info:
            print(f"{base_msg}, {extra_info}")
        else:
            print(base_msg)

    @classmethod
    def print_improvement(
        cls,
        iteration: int,
        old_penalty: float,
        new_penalty: float,
        improvement_type: str = "Improvement",
    ) -> None:
        """Print improvement-based progress update with improvement amount."""
        improvement = old_penalty - new_penalty
        improvement_pct = (improvement / old_penalty * 100) if old_penalty > 0 else 0
        print(
            f"Iteration {iteration:4d}, {improvement_type}! "
            f"Penalty: {old_penalty:.2f} → {new_penalty:.2f} "
            f"(↓{improvement:.2f}, {improvement_pct:.1f}%)"
        )

    @classmethod
    def print_generation_progress(
        cls,
        generation: int,
        best_penalty: float,
        avg_fitness: float,
    ) -> None:
        """Print standardized progress update for genetic algorithm generations."""
        print(
            f"Generation {generation:4d}, "
            f"Best Penalty = {best_penalty:.2f}, Avg Fitness = {avg_fitness:.4f}"
        )

    @classmethod
    def print_restart_progress(cls, restart: int, max_restarts: int) -> None:
        """Print standardized progress update for random restart variants."""
        print(f"Restart {restart:3d}/{max_restarts}")

    @classmethod
    def print_perfect_solution(
        cls, iteration_or_generation: int, algorithm_type: str = "iteration"
    ) -> None:
        """Print perfect solution found message."""
        print(f"Perfect solution found at {algorithm_type} {iteration_or_generation}!")

    @classmethod
    def calculate_improvement_stats(
        cls, initial_penalty: float, best_penalty: float
    ) -> tuple[float, float]:
        """Calculate improvement amount and percentage."""
        improvement = initial_penalty - best_penalty
        improvement_pct = (
            (improvement / initial_penalty * 100) if initial_penalty > 0 else 0
        )
        return improvement, improvement_pct

    @classmethod
    def print_algorithm_completion(
        cls,
        algorithm_name: str,
        results: Dict[str, Any],
        initial_penalty: float,
        duration: Optional[float] = None,
    ) -> None:
        """Print standardized algorithm completion summary."""
        print(cls.SEPARATOR)
        print(f"{algorithm_name} completed!")

        # Core metrics (common to all algorithms)
        if "iterations" in results:
            print(f"Iterations: {results['iterations']}")
        if duration is not None:
            print(f"Duration: {duration:.2f} seconds")
        elif "duration" in results:
            print(f"Duration: {results['duration']:.2f} seconds")

        print(f"Initial Penalty: {initial_penalty:.2f}")
        print(f"Best Penalty: {results['best_penalty']:.2f}")

        # Calculate and display improvement
        improvement, improvement_pct = cls.calculate_improvement_stats(
            initial_penalty, results["best_penalty"]
        )
        print(f"Improvement: {improvement:.2f} ({improvement_pct:.1f}%)")

        # Algorithm-specific metrics
        cls._print_algorithm_specific_metrics(algorithm_name, results)

        print(cls.SEPARATOR)

    @classmethod
    def _print_algorithm_specific_metrics(
        cls, algorithm_name: str, results: Dict[str, Any]
    ) -> None:
        """Print algorithm-specific metrics in the completion summary."""
        algorithm_lower = algorithm_name.lower()

        if "genetic" in algorithm_lower:
            pass

        elif "hill climbing" in algorithm_lower:
            variant = results.get("variant", "")
            if variant == "random_restart" and "restarts" in results:
                print(f"Restarts: {results['restarts']}")
            if variant == "sideways_move" and "sideways_moves_taken" in results:
                print(f"Sideways Moves: {results['sideways_moves_taken']}")

        elif "simulated annealing" in algorithm_lower:
            if "local_optima_count" in results:
                print(f"Local Optima: {results['local_optima_count']}")


class ProgressTracker:
    """Helper class for consistent progress reporting intervals."""

    @classmethod
    def should_report_progress(
        cls, current: int, total: int, interval_pct: float = 10.0
    ) -> bool:
        """Check if progress should be reported based on percentage intervals."""
        if current == 0 or total <= 0:
            return False

        interval = max(1, int(total * (interval_pct / 100.0)))
        return current % interval == 0


class ResultFormatter:
    """Utility class for formatting algorithm results consistently."""

    @classmethod
    def format_penalty(cls, penalty: float, decimal_places: int = 2) -> str:
        """Format penalty value consistently."""
        return f"{penalty:.{decimal_places}f}"

    @classmethod
    def format_percentage(cls, percentage: float, decimal_places: int = 1) -> str:
        """Format percentage value consistently."""
        return f"{percentage:.{decimal_places}f}%"

    @classmethod
    def format_duration(cls, seconds: float) -> str:
        """Format duration in human-readable format."""
        if seconds < 1:
            return f"{seconds:.3f} seconds"
        elif seconds < 60:
            return f"{seconds:.2f} seconds"
        else:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.1f}s"

    @classmethod
    def format_iteration_count(cls, iterations: int) -> str:
        """Format iteration count with appropriate grouping."""
        if iterations >= 1000:
            return f"{iterations:,}"
        else:
            return str(iterations)


# Convenience functions for backward compatibility and ease of use
def print_start(algorithm_name: str, **parameters) -> None:
    """Convenience function to print algorithm start message."""
    AlgorithmOutputFormatter.print_algorithm_start(algorithm_name, parameters)


def print_initial(state: State, penalty: float, title: str = "Initial State") -> None:
    """Convenience function to print initial state."""
    AlgorithmOutputFormatter.print_initial_state(state, penalty, title)


def print_progress(
    iteration: int,
    best_penalty: float,
    extra_info: Optional[str] = None,
) -> None:
    """Convenience function to print progress update."""
    AlgorithmOutputFormatter.print_progress(iteration, best_penalty, extra_info)


def print_completion(
    algorithm_name: str,
    results: Dict[str, Any],
    initial_penalty: float,
    duration: Optional[float] = None,
) -> None:
    """Convenience function to print completion summary."""
    AlgorithmOutputFormatter.print_algorithm_completion(
        algorithm_name, results, initial_penalty, duration
    )


def print_improvement(
    iteration: int,
    old_penalty: float,
    new_penalty: float,
    improvement_type: str = "Improvement",
) -> None:
    """Convenience function to print improvement update."""
    AlgorithmOutputFormatter.print_improvement(
        iteration, old_penalty, new_penalty, improvement_type
    )
