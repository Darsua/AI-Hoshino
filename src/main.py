import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.main.objective import ObjectiveFunction
from src.algorithms import run_genetic_algorithm, HillClimbing, SimulatedAnnealing
from src.main import State

import argparse

def main():
    arg_parser = argparse.ArgumentParser(description="AI-Hoshino: A scheduling problem solver")
    arg_parser.add_argument('input_file', type=str, nargs='?', default=None, help='Path to the input JSON file (required for CLI mode)')
    arg_parser.add_argument('--gui', action='store_true', help='Launch the graphical user interface')
    arg_parser.add_argument('--genetic', action='store_true', help='Use genetic algorithm for optimization')
    arg_parser.add_argument('--simulated-annealing', '--sa', action='store_true', help='Use simulated annealing algorithm for optimization')
    arg_parser.add_argument('--generations', type=int, default=100, help='Number of generations for genetic algorithm (default: 100)')
    arg_parser.add_argument('--population', type=int, default=50, help='Population size for genetic algorithm (default: 50)')
    arg_parser.add_argument('--initial-temp', type=float, default=500.0, help='Initial temperature for simulated annealing (default: 500.0)')
    arg_parser.add_argument('--cooling-rate', type=float, default=0.97, help='Cooling rate for simulated annealing (default: 0.97)')
    arg_parser.add_argument('--max-iterations', type=int, default=5000, help='Maximum iterations for simulated annealing (default: 5000)')
    arg_parser.add_argument('--plot', action='store_true', help='Generate visualization plots (for simulated annealing)')
    arg_parser.add_argument('--hc', action='store_true', help='Use Hill Climbing algorithm for optimization')
    arg_parser.add_argument('--hc-variant', type=str, default='steepest_ascent', choices=['stochastic', 'steepest_ascent', 'sideways_move', 'random_restart'], help='Variant of Hill Climbing to use')
    arg_parser.add_argument('--num-neighbors', type=int, default=10, help='Number of neighbors to check for Steepest Ascent Hill Climbing')
    arg_parser.add_argument('--max-sideways-moves', type=int, default=100, help='Maximum sideways moves allowed in Hill Climbing')
    arg_parser.add_argument('--max-restarts', type=int, default=10, help='Maximum restarts for Random Restart Hill Climbing')
    arg_parser.add_argument('--hc-restart-variant', type=str, default='steepest_ascent', choices=['stochastic', 'steepest_ascent', 'sideways_move'], help='Hill Climbing variant to use within Random Restart')

    args = arg_parser.parse_args()

    if args.gui:
        from src.gui import SchedulerGUI
        app = SchedulerGUI()
        app.mainloop()
    else:
        if not args.input_file:
            print("Error: input_file is required when not using --gui mode.")
            arg_parser.print_help()
            exit(1)

        from src.utils.parser import load_input
        try:
            classes, rooms, students = load_input(args.input_file)
        except (FileNotFoundError, ValueError) as e:
            print(e)
            exit(1)

        # DEBUG: Test print
        for cls_code, cls in classes.items():
            print(f"Class {cls_code}: {cls.studentCount} students, {cls.credits} credits")
            i = 1
            for student in cls.students:
                print(f" {i}. {student.id}: Priority = {student.classes.index(cls_code) + 1}")
                i = i + 1
            print()
        for room_code, room in rooms.items():
            print(f"Room {room_code}: Capacity {room.capacity}")
        print()
        for student_id, student in students.items():
            print(f"Student {student_id}: Classes {student.classes}")

        if args.genetic:
            print("\nRunning Genetic Algorithm optimization...")
            best_state = run_genetic_algorithm(
                classes,
                rooms,
                population_size=args.population,
                generations=args.generations
            )
            print("\nBest schedule found:")
            print(best_state)
            print(f"Final penalty: {ObjectiveFunction().calculate(best_state)}")
        elif args.simulated_annealing:
            from src.algorithms.simulated_annealing import SimulatedAnnealing
            
            print("\n" + "=" * 70)
            print("SIMULATED ANNEALING OPTIMIZATION")
            print("=" * 70)
            
            objective_func = ObjectiveFunction(
                student_conflict=True,
                room_conflict=True,
                capacity=True
            )
            
            sa = SimulatedAnnealing(
                classes=classes,
                rooms=rooms,
                objective_function=objective_func,
                initial_temp=args.initial_temp,
                cooling_rate=args.cooling_rate,
                min_temp=0.01,
                max_iterations=args.max_iterations
            )
            
            print(f"Configuration:")
            print(f"  Initial Temperature: {args.initial_temp}")
            print(f"  Cooling Rate: {args.cooling_rate}")
            print(f"  Max Iterations: {args.max_iterations}")
            print()
            
            best_state, results = sa.run(verbose=True)
            
            print("\n" + "=" * 70)
            print("OPTIMIZATION RESULTS")
            print("=" * 70)
            print(f"Initial Penalty:  {results['initial_penalty']:.2f}")
            print(f"Best Penalty:     {results['best_penalty']:.2f}")
            print(f"Final Penalty:    {results['final_penalty']:.2f}")
            print(f"Improvement:      {results['initial_penalty'] - results['best_penalty']:.2f} "
                  f"({(results['initial_penalty'] - results['best_penalty']) / results['initial_penalty'] * 100:.1f}%)")
            print(f"Iterations:       {results['iterations']}")
            print(f"Duration:         {results['duration']:.2f} seconds")
            print(f"Times Stuck:      {results['local_optima_count']}")
            print("=" * 70)
            
            print("\nBest Schedule Found:")
            print(best_state)
            
            if args.plot:
                print("\nGenerating visualization plots...")
                figures = sa.plot_results(results, show=True)  # Show plots in CLI
                print(f"✓ {len(figures)} plots displayed")

        elif args.hc:
            from src.algorithms.hill_climb import HillClimbing
            from src.main.state import State

            print("\n" + "=" * 70)
            print("HILL CLIMBING OPTIMIZATION")
            print("=" * 70)

            objective_func = ObjectiveFunction(
                student_conflict=True,
                room_conflict=True,
                capacity=True
            )

            initial_state = State()
            initial_state.random_fill(classes, rooms)
            initial_penalty = objective_func.calculate(initial_state)
            
            print("Initial State (Random Schedule):")
            print(initial_state)
            print(f"Initial Penalty: {initial_penalty:.2f}")
            print("-" * 70)

            hc = HillClimbing(
                objective_function=objective_func,
                rooms=rooms,
                classes=classes
            )

            print(f"Configuration:")
            print(f"  Variant: {args.hc_variant}")
            print(f"  Max Iterations: {args.max_iterations}")
            if args.hc_variant == 'steepest_ascent':
                print(f"  Neighbors to check: {args.num_neighbors}")
            if args.hc_variant == 'sideways_move':
                print(f"  Max Sideways Moves: {args.max_sideways_moves}")
            if args.hc_variant == 'random_restart':
                print(f"  Max Restarts: {args.max_restarts}")
                print(f"  Restart Variant: {args.hc_restart_variant}")
            print()

            best_state, results = hc.solve(
                initial_state=initial_state,
                variant=args.hc_variant,
                max_iterations=args.max_iterations,
                num_neighbors=args.num_neighbors,
                max_sideways_moves=args.max_sideways_moves,
                max_restarts=args.max_restarts,
                restart_variant=args.hc_restart_variant
            )

            print("\n" + "=" * 70)
            print("OPTIMIZATION RESULTS")
            print("=" * 70)
            print(f"Initial Penalty:  {initial_penalty:.2f}")
            print(f"Best Penalty:     {results['best_penalty']:.2f}")
            print(f"Improvement:      {initial_penalty - results['best_penalty']:.2f} "
                  f"({(initial_penalty - results['best_penalty']) / initial_penalty * 100:.1f}%)")
            print(f"Total Iterations: {results['iterations']}")
            if args.hc_variant == 'random_restart':
                print(f"Restarts:         {results['restarts']}")
                print(f"Avg Iter/Restart: {sum(results['iterations_per_restart']) / len(results['iterations_per_restart']):.1f}")
            if args.hc_variant == 'sideways_move':
                print(f"Sideways Moves:   {results.get('sideways_moves_taken', 0)}")
            print(f"Duration:         {results['duration']:.2f} seconds")
            print("=" * 70)

            print("\nFinal State (Best Schedule Found):")
            print(best_state)

            if args.plot:
                print("\nGenerating visualization plots...")
                fig = hc.plot_results(results, show=True)  # Show plot in CLI
                print("✓ Plot displayed")

        else:
            from src.main.state import State
            state = State()
            state.random_fill(classes, rooms)
            print("Random schedule:")
            print(state)
            print(f"Random schedule penalty: {ObjectiveFunction().calculate(state)}")

if __name__ == "__main__":
    main()
