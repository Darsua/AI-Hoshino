"""
Help content for AI-Hoshino Course Scheduler GUI
"""

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
  Num Neighbors        Number of neighbors to evaluate (Steepest Ascent)
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
