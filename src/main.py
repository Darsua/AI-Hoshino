import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.main.objective import ObjectiveFunction
from src.algorithms import run_genetic_algorithm, HillClimbing, SimulatedAnnealing
from src.main import State

import argparse


def main():
    parser = argparse.ArgumentParser(
        description="AI-Hoshino: A scheduling problem solver",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --gui                                   # Launch GUI
  %(prog)s input.json --genetic --population 100   # Run genetic algorithm
  %(prog)s input.json --sa --plot                  # Run simulated annealing with plots
  %(prog)s input.json --hc --hc-variant stochastic # Run hill climbing
        """,
    )

    # Required input file (except when using GUI)
    parser.add_argument(
        "input_file",
        type=str,
        nargs="?",
        default=None,
        help="Path to the input JSON file (required for CLI mode)",
    )

    # Interface mode
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the graphical user interface",
    )

    # Algorithm selection (mutually exclusive)
    algo_group = parser.add_mutually_exclusive_group()
    algo_group.add_argument(
        "--genetic",
        action="store_true",
        help="Use genetic algorithm for optimization",
    )
    algo_group.add_argument(
        "--sa",
        action="store_true",
        help="Use simulated annealing algorithm for optimization",
    )
    algo_group.add_argument(
        "--hc",
        action="store_true",
        help="Use Hill Climbing algorithm for optimization",
    )

    # Genetic Algorithm parameters
    genetic_group = parser.add_argument_group("Genetic Algorithm Parameters")
    genetic_group.add_argument(
        "--population",
        type=int,
        default=32,
        metavar="N",
        help="Population size (default: %(default)s)",
    )
    genetic_group.add_argument(
        "--generations",
        type=int,
        default=100,
        metavar="N",
        help="Number of generations (default: %(default)s)",
    )

    # Simulated Annealing parameters
    sa_group = parser.add_argument_group("Simulated Annealing Parameters")
    sa_group.add_argument(
        "--initial-temp",
        type=float,
        default=500.0,
        metavar="TEMP",
        help="Initial temperature (default: %(default)s)",
    )
    sa_group.add_argument(
        "--cooling-rate",
        type=float,
        default=0.97,
        metavar="RATE",
        help="Cooling rate (default: %(default)s)",
    )
    sa_group.add_argument(
        "--max-iterations",
        type=int,
        default=5000,
        metavar="N",
        help="Maximum iterations for SA (default: %(default)s), for HC use specific HC parameters",
    )

    # Hill Climbing parameters
    hc_group = parser.add_argument_group("Hill Climbing Parameters")
    hc_group.add_argument(
        "--hc-variant",
        type=str,
        default="steepest_ascent",
        choices=["stochastic", "steepest_ascent", "sideways_move", "random_restart"],
        metavar="VARIANT",
        help="Hill Climbing variant (choices: %(choices)s, default: %(default)s)",
    )
    hc_group.add_argument(
        "--num-neighbors",
        type=int,
        default=10,
        metavar="N",
        help="Number of neighbors to check for Steepest Ascent (default: %(default)s)",
    )
    hc_group.add_argument(
        "--hc-max-iterations",
        type=int,
        default=100,
        metavar="N",
        help="Maximum iterations for Hill Climbing (default: %(default)s)",
    )
    hc_group.add_argument(
        "--max-sideways-moves",
        type=int,
        default=100,
        metavar="N",
        help="Maximum sideways moves for sideways_move variant (default: %(default)s)",
    )
    hc_group.add_argument(
        "--max-restarts",
        type=int,
        default=10,
        metavar="N",
        help="Maximum restarts for random_restart variant (default: %(default)s)",
    )
    hc_group.add_argument(
        "--hc-restart-variant",
        type=str,
        default="steepest_ascent",
        choices=["stochastic", "steepest_ascent", "sideways_move"],
        metavar="VARIANT",
        help="Hill Climbing variant to use within Random Restart (choices: %(choices)s, default: %(default)s)",
    )

    # General options
    general_group = parser.add_argument_group("General Options")
    general_group.add_argument(
        "--plot",
        action="store_true",
        help="Generate and display visualization plots",
    )

    args = parser.parse_args()

    if args.gui:
        from src.gui import SchedulerGUI

        app = SchedulerGUI()
        app.mainloop()
    else:
        if not args.input_file:
            print("Error: input_file is required when not using --gui mode.")
            parser.print_help()
            exit(1)

        from src.utils.parser import load_input

        try:
            classes, rooms, students = load_input(args.input_file)
        except (FileNotFoundError, ValueError) as e:
            print(e)
            exit(1)

        # Print summary of loaded data
        print(
            f"Loaded {len(classes)} classes, {len(rooms)} rooms, {len(students)} students from {args.input_file}\n"
        )

        if args.genetic:
            from src.algorithms.genetic import GeneticAlgorithm

            ga = GeneticAlgorithm(
                population_size=args.population, generations=args.generations
            )

            best_state, results = ga.optimize(classes, rooms)

            print(f"\nFinal Schedule:")
            print(best_state)

            if args.plot:
                fig = ga.plot_results(results, show=True)

        elif args.sa:
            from src.algorithms.simulated_annealing import SimulatedAnnealing
            from src.main.objective import ObjectiveFunction

            objective_func = ObjectiveFunction(
                student_conflict=True, room_conflict=True, capacity=True
            )

            sa = SimulatedAnnealing(
                classes=classes,
                rooms=rooms,
                objective_function=objective_func,
                initial_temp=args.initial_temp,
                cooling_rate=args.cooling_rate,
                min_temp=0.01,
                max_iterations=args.max_iterations,
            )

            best_state, results = sa.run(verbose=True)

            print(f"\nFinal Schedule:")
            print(best_state)

            if args.plot:
                figures = sa.plot_results(results, show=True)

        elif args.hc:
            from src.algorithms.hill_climb import HillClimbing
            from src.main.state import State
            from src.main.objective import ObjectiveFunction

            objective_func = ObjectiveFunction(
                student_conflict=True, room_conflict=True, capacity=True
            )

            initial_state = State()
            initial_state.random_fill(classes, rooms)

            hc = HillClimbing(
                objective_function=objective_func, rooms=rooms, classes=classes
            )

            # Use specific HC max iterations, fallback to 1000 for stochastic variant
            hc_max_iter = args.hc_max_iterations
            if args.hc_variant == "stochastic" and hc_max_iter == 100:
                hc_max_iter = 1000

            best_state, results = hc.solve(
                initial_state=initial_state,
                variant=args.hc_variant,
                max_iterations=hc_max_iter,
                num_neighbors=args.num_neighbors,
                max_sideways_moves=args.max_sideways_moves,
                max_restarts=args.max_restarts,
                restart_variant=args.hc_restart_variant,
            )

            print(f"\nFinal Schedule:")
            print(best_state)

            if args.plot:
                fig = hc.plot_results(results, show=True)

        else:
            from src.main.state import State
            from src.main.objective import ObjectiveFunction

            state = State()
            state.random_fill(classes, rooms)
            penalty = ObjectiveFunction().calculate(state)
            print(f"\nRandom Schedule (Penalty: {penalty:.2f}):")
            print(state)


if __name__ == "__main__":
    main()
