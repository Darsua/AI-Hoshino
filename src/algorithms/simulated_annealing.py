import random
import time
import math
import copy
from typing import Tuple, List, Dict

# Optional matplotlib import for plotting
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from src.main.state import State
from src.main.objective import ObjectiveFunction
from src.models import CourseClass, Room, TimeSlot


class SimulatedAnnealing:
    def __init__(
        self,
        classes: Dict[str, CourseClass],
        rooms: Dict[str, Room],
        objective_function: ObjectiveFunction,
        initial_temp: float = 500.0,
        cooling_rate: float = 0.97,
        min_temp: float = 0.01,
        max_iterations: int = 10000
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
        
    def generate_neighbor(self, current_state: State) -> State:
        neighbor = State()
        # Deep copy meetings
        neighbor.meetings = [
            State.Allocation(
                meeting.course_class,
                TimeSlot(
                    meeting.time_slot.day,
                    meeting.time_slot.start_hour,
                    meeting.time_slot.end_hour
                ),
                meeting.room
            )
            for meeting in current_state.meetings
        ]
        
        if len(neighbor.meetings) < 2:
            return neighbor
        
        # Choose random operation
        operation = random.choice(['swap', 'move'])
        
        if operation == 'swap' and len(neighbor.meetings) >= 2:
            # Swap time slots and rooms of two random meetings
            idx1, idx2 = random.sample(range(len(neighbor.meetings)), 2)
            meeting1 = neighbor.meetings[idx1]
            meeting2 = neighbor.meetings[idx2]
            
            # Swap time slots
            meeting1.time_slot, meeting2.time_slot = meeting2.time_slot, meeting1.time_slot
            # Swap rooms
            meeting1.room, meeting2.room = meeting2.room, meeting1.room
            
        else:  # move
            # Move a random meeting to a new time slot and room
            idx = random.randint(0, len(neighbor.meetings) - 1)
            meeting = neighbor.meetings[idx]
            
            # Generate new time slot
            day = TimeSlot.Day(random.randint(0, 4))
            start_hour = random.randint(7, 17)
            duration = meeting.time_slot.duration()
            end_hour = min(start_hour + duration, 18)
            
            meeting.time_slot = TimeSlot(day, start_hour, end_hour)
            
            # Assign new room
            room_list = list(self.rooms.values())
            meeting.room = random.choice(room_list)
        
        return neighbor
    
    def acceptance_probability(self, current_penalty: float, neighbor_penalty: float, temperature: float) -> float:
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
            print(f"Starting Simulated Annealing...")
            print(f"Initial penalty: {initial_penalty:.2f}")
            print(f"Initial temperature: {temperature:.2f}")
            print(f"Cooling rate: {self.cooling_rate}")
            print("-" * 60)
        
        # Main loop
        while temperature > self.min_temp and iteration < self.max_iterations:
            # Generate neighbor
            neighbor_state = self.generate_neighbor(current_state)
            neighbor_penalty = self.objective_function.calculate(neighbor_state)
            
            # Calculate acceptance probability
            accept_prob = self.acceptance_probability(current_penalty, neighbor_penalty, temperature)
            self.acceptance_prob_history.append(accept_prob)
            
            # Decide whether to accept neighbor
            if random.random() < accept_prob:
                current_state = neighbor_state
                current_penalty = neighbor_penalty
                
                # Update best solution if improved
                if current_penalty < best_penalty:
                    best_state = copy.deepcopy(current_state)
                    best_penalty = current_penalty
            
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
            
            # Print progress
            if verbose and (iteration + 1) % 500 == 0:
                print(f"Iteration {iteration + 1}: "
                      f"Current Penalty = {current_penalty:.2f}, "
                      f"Best Penalty = {best_penalty:.2f}, "
                      f"Temperature = {temperature:.4f}")
            
            iteration += 1
        
        end_time = time.time()
        duration = end_time - start_time
        
        if verbose:
            print("-" * 60)
            print(f"Simulated Annealing completed!")
            print(f"Iterations: {iteration}")
            print(f"Duration: {duration:.2f} seconds")
            print(f"Initial penalty: {initial_penalty:.2f}")
            print(f"Final penalty: {current_penalty:.2f}")
            print(f"Best penalty: {best_penalty:.2f}")
            print(f"Improvement: {initial_penalty - best_penalty:.2f} "
                  f"({(initial_penalty - best_penalty) / initial_penalty * 100:.1f}%)")
            print(f"Times stuck in local optima: {self.local_optima_count}")
        
        results = {
            'initial_state': initial_state,
            'final_state': current_state,
            'best_state': best_state,
            'initial_penalty': initial_penalty,
            'final_penalty': current_penalty,
            'best_penalty': best_penalty,
            'iterations': iteration,
            'duration': duration,
            'objective_history': self.objective_history,
            'acceptance_prob_history': self.acceptance_prob_history,
            'temperature_history': self.temperature_history,
            'best_objective_history': self.best_objective_history,
            'local_optima_count': self.local_optima_count,
            'iterations_stuck': self.iterations_stuck
        }
        
        return best_state, results
    
    def plot_results(self, results: Dict, save_path: str = None):
        if not MATPLOTLIB_AVAILABLE:
            print("Warning: matplotlib not available. Install it to generate plots:")
            print("  pip install matplotlib")
            return None
            
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Simulated Annealing Optimization Results', fontsize=16, fontweight='bold')
        
        iterations = range(len(results['objective_history']))
        
        # Plot 1: Objective Value vs Iterations
        ax1 = axes[0, 0]
        ax1.plot(iterations, results['objective_history'], 
                label='Current Penalty', alpha=0.7, linewidth=1)
        ax1.plot(iterations, results['best_objective_history'], 
                label='Best Penalty', color='green', linewidth=2)
        
        # Mark local optima points
        if results['iterations_stuck']:
            stuck_iterations = results['iterations_stuck']
            stuck_penalties = [results['objective_history'][i] for i in stuck_iterations]
            ax1.scatter(stuck_iterations, stuck_penalties, 
                       color='red', s=100, marker='x', 
                       label=f"Stuck in Local Optima ({results['local_optima_count']}x)",
                       zorder=5)
        
        ax1.set_xlabel('Iteration')
        ax1.set_ylabel('Penalty (Objective Value)')
        ax1.set_title('Objective Value vs Iterations')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Acceptance Probability vs Iterations
        ax2 = axes[0, 1]
        acceptance_iterations = range(len(results['acceptance_prob_history']))
        ax2.plot(acceptance_iterations, results['acceptance_prob_history'], 
                color='orange', alpha=0.6, linewidth=1)
        ax2.set_xlabel('Iteration')
        ax2.set_ylabel('Acceptance Probability (e^(ΔE/T))')
        ax2.set_title('Acceptance Probability vs Iterations')
        ax2.set_ylim(-0.05, 1.05)
        ax2.grid(True, alpha=0.3)
        
        # Add statistics to acceptance probability plot
        avg_accept = sum(results['acceptance_prob_history']) / len(results['acceptance_prob_history'])
        ax2.axhline(y=avg_accept, color='red', linestyle='--', 
                   label=f'Average: {avg_accept:.3f}')
        ax2.legend()
        
        # Plot 3: Temperature vs Iterations
        ax3 = axes[1, 0]
        temp_iterations = range(len(results['temperature_history']))
        ax3.plot(temp_iterations, results['temperature_history'], 
                color='purple', linewidth=2)
        ax3.set_xlabel('Iteration')
        ax3.set_ylabel('Temperature')
        ax3.set_title('Temperature vs Iterations (Cooling Schedule)')
        ax3.grid(True, alpha=0.3)
        ax3.set_yscale('log')  # Log scale to better visualize exponential decay
        
        # Plot 4: Summary Statistics
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        summary_text = f"""
        OPTIMIZATION SUMMARY
        {'=' * 40}
        
        Initial Penalty:     {results['initial_penalty']:.2f}
        Final Penalty:       {results['final_penalty']:.2f}
        Best Penalty:        {results['best_penalty']:.2f}
        
        Improvement:         {results['initial_penalty'] - results['best_penalty']:.2f}
        Improvement %:       {(results['initial_penalty'] - results['best_penalty']) / results['initial_penalty'] * 100:.1f}%
        
        Total Iterations:    {results['iterations']}
        Duration:            {results['duration']:.2f} seconds
        
        Initial Temperature: {self.initial_temp:.2f}
        Final Temperature:   {results['temperature_history'][-1]:.4f}
        Cooling Rate:        {self.cooling_rate}
        
        Local Optima Count:  {results['local_optima_count']}
        Stuck at Iterations: {results['iterations_stuck'][:5]}
                             {'...' if len(results['iterations_stuck']) > 5 else ''}
        """
        
        ax4.text(0.1, 0.5, summary_text, fontsize=11, family='monospace',
                verticalalignment='center')
        
        plt.tight_layout()
        
        # Commented out for GUI integration - graphs will be displayed, not saved
        # if save_path:
        #     plt.savefig(save_path, dpi=300, bbox_inches='tight')
        #     print(f"Plot saved to {save_path}")
        
        plt.show()
        
        return fig
    
    def plot_acceptance_probability_detail(self, results: Dict, save_path: str = None):
        if not MATPLOTLIB_AVAILABLE:
            print("Warning: matplotlib not available. Install it to generate plots:")
            print("  uv add matplotlib")
            return None
            
        fig, ax = plt.subplots(figsize=(12, 6))
        
        acceptance_probs = results['acceptance_prob_history']
        iterations = range(len(acceptance_probs))
        
        # Create scatter plot with color gradient
        scatter = ax.scatter(iterations, acceptance_probs, 
                           c=acceptance_probs, cmap='RdYlGn',
                           s=10, alpha=0.6)
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Acceptance Probability', rotation=270, labelpad=20)
        
        # Add threshold lines
        ax.axhline(y=0.5, color='blue', linestyle='--', alpha=0.5, 
                  label='50% Acceptance')
        ax.axhline(y=0.1, color='orange', linestyle='--', alpha=0.5, 
                  label='10% Acceptance')
        
        ax.set_xlabel('Iteration', fontsize=12)
        ax.set_ylabel('Acceptance Probability e^(ΔE/T)', fontsize=12)
        ax.set_title('Detailed View: Acceptance Probability Over Iterations', 
                    fontsize=14, fontweight='bold')
        ax.set_ylim(-0.05, 1.05)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add statistics
        total_accepts = sum(1 for p in acceptance_probs if random.random() < p)
        accept_rate = len([p for p in acceptance_probs if p > 0.5]) / len(acceptance_probs) * 100
        
        stats_text = f"High Acceptance Rate (>50%): {accept_rate:.1f}%\n"
        stats_text += f"Mean Acceptance Prob: {sum(acceptance_probs) / len(acceptance_probs):.3f}"
        
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
               fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        # Commented out for GUI integration - graphs will be displayed, not saved
        # if save_path:
        #     plt.savefig(save_path, dpi=300, bbox_inches='tight')
        #     print(f"Acceptance probability detail plot saved to {save_path}")
        
        plt.show()
        
        return fig
