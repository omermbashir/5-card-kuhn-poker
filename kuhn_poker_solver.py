"""
5-Card Kuhn Poker Solver
Based on "Bot Naurazia" from Omer Bashir's Masters Thesis
Converts R implementation to Python

This implements an iterative algorithm to approximate Nash equilibrium
strategies for 5-card Kuhn Poker through self-play.
"""

import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Any
import copy


class KuhnPokerEngine:
    """
    Engine for simulating 5-card Kuhn Poker games.
    Handles game logic and payoff calculations.
    """
    
    def __init__(self, n: int = 5):
        """
        Initialize the poker engine.
        
        Args:
            n: Number of cards in the deck (default 5 for 5-card Kuhn)
        """
        self.n = n
        
    def player_1_action(self, action: int, stack_1: float, pot: float, 
                       iteration: int) -> Tuple[float, float]:
        """
        Process Player 1's action and update stacks/pot.
        
        Args:
            action: 1=bet, 2=check, 3=fold
            stack_1: Player 1's current stack
            pot: Current pot size
            iteration: 1 for first node, 2 for final node
            
        Returns:
            Tuple of (new_stack_1, new_pot)
        """
        if iteration == 1:  # First node
            stack_1 -= 1  # Ante
            pot += 1
            if action == 1:  # Bet
                stack_1 -= 1
                pot += 1
        elif iteration == 2:  # Second node (call/fold)
            if action == 2:  # Call
                stack_1 -= 1
                pot += 1
            # Fold doesn't change stack or pot at this node
                
        return stack_1, pot
    
    def player_2_action(self, action: int, stack_2: float, pot: float, 
                       iteration: int) -> Tuple[float, float]:
        """
        Process Player 2's action and update stacks/pot.
        
        Args:
            action: 1=bet, 2=check/call, 3=fold
            stack_2: Player 2's current stack
            pot: Current pot size
            iteration: 1 for left node (bet/check), 2 for right node (call/fold)
            
        Returns:
            Tuple of (new_stack_2, new_pot)
        """
        stack_2 -= 1  # Ante
        pot += 1
        
        if iteration == 1:  # Bet/check node
            if action == 1:  # Bet
                stack_2 -= 1
                pot += 1
        elif iteration == 2:  # Call/fold node
            if action == 2:  # Call
                stack_2 -= 1
                pot += 1
                
        return stack_2, pot
    
    def showdown(self, stack_1: float, stack_2: float, hand_1: int, 
                hand_2: int, pot: float) -> Tuple[float, float]:
        """
        Determine winner at showdown and distribute pot.
        
        Args:
            stack_1: Player 1's stack
            stack_2: Player 2's stack
            hand_1: Player 1's card
            hand_2: Player 2's card
            pot: Current pot size
            
        Returns:
            Tuple of (final_stack_1, final_stack_2)
        """
        if hand_1 > hand_2:
            return stack_1 + pot, stack_2
        else:
            return stack_1, stack_2 + pot
    
    def run_game(self, action_1a: int, action_1b: int, action_2a: int, 
                action_2b: int, hand_1: int, hand_2: int) -> Tuple[float, float]:
        """
        Run a complete game and return final payoffs.
        
        Args:
            action_1a: Player 1's first action (1=bet, 2=check)
            action_1b: Player 1's second action (2=call, 3=fold) - only if P1 checks first
            action_2a: Player 2's action in left node (1=bet, 2=check) - only if P1 checks
            action_2b: Player 2's action in right node (2=call, 3=fold) - only if P1 bets
            hand_1: Player 1's card
            hand_2: Player 2's card
            
        Returns:
            Tuple of (stack_1, stack_2) - net payoffs for each player
        """
        stack_1, stack_2 = 0.0, 0.0
        pot = 0.0
        
        # Player 1's first action
        stack_1, pot = self.player_1_action(action_1a, stack_1, pot, 1)
        
        if action_1a == 3:  # P1 folds (shouldn't happen in first node but included for completeness)
            stack_2 += pot
        elif action_1a == 2:  # P1 checks
            # Player 2's turn in left node
            stack_2, pot = self.player_2_action(action_2a, stack_2, pot, 1)
            
            if action_2a == 1:  # P2 bets after P1 checks
                # Player 1's second action (call or fold)
                stack_1, pot = self.player_1_action(action_1b, stack_1, pot, 2)
                
                if action_1b == 2:  # P1 calls
                    stack_1, stack_2 = self.showdown(stack_1, stack_2, hand_1, hand_2, pot)
                elif action_1b == 3:  # P1 folds
                    stack_2 += pot
            elif action_2a == 2:  # P2 checks
                # Both check, go to showdown
                stack_1, stack_2 = self.showdown(stack_1, stack_2, hand_1, hand_2, pot)
                
        elif action_1a == 1:  # P1 bets
            # Player 2's turn in right node
            stack_2, pot = self.player_2_action(action_2b, stack_2, pot, 2)
            
            if action_2b == 2:  # P2 calls
                stack_1, stack_2 = self.showdown(stack_1, stack_2, hand_1, hand_2, pot)
            elif action_2b == 3:  # P2 folds
                stack_1 += pot
                
        return stack_1, stack_2


class StrategyManager:
    """
    Manages strategy matrices for both players.
    Strategy matrix format:
    - Player 1: 5 rows (Check1, Bet, Fold1, Fold2, Call) x n columns (cards)
    - Player 2: 4 rows (Bet/Check, Check/Fold, Call, Fold) x n columns (cards)
    """
    
    def __init__(self, n: int = 5):
        """
        Initialize strategy manager.
        
        Args:
            n: Number of cards in deck
        """
        self.n = n
        
    def create_strategy_matrix(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Create empty strategy matrices for both players.
        
        Returns:
            Tuple of (player1_strategy, player2_strategy) as DataFrames
        """
        # Player 1 strategy matrix
        strategy_1 = pd.DataFrame(
            np.zeros((5, self.n)),
            index=['P(Check 1)', 'P(Bet)', 'P(Fold 1)', 'P(Fold 2)', 'P(Call)'],
            columns=[f'Card_{i+1}' for i in range(self.n)]
        )
        
        # Player 2 strategy matrix
        strategy_2 = pd.DataFrame(
            np.zeros((4, self.n)),
            index=['P(Bet/Check)', 'P(Check/Fold)', 'P(Call)', 'P(Fold)'],
            columns=[f'Card_{i+1}' for i in range(self.n)]
        )
        
        return strategy_1, strategy_2
    
    def initialize_default_strategy(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Initialize with default starting strategies based on the thesis.
        
        Returns:
            Tuple of initialized strategy matrices
        """
        p1_strat, p2_strat = self.create_strategy_matrix()
        
        # Player 1 fixed strategies
        # Always call with highest card
        p1_strat.iloc[4, self.n-1] = 1.0  # Call with 5
        p1_strat.iloc[3, self.n-1] = 0.0  # Don't fold with 5
        
        # Never call with lowest card
        p1_strat.iloc[4, 0] = 0.0  # Don't call with 1
        p1_strat.iloc[3, 0] = 1.0  # Always fold with 1
        
        # Turn off folding in first node
        p1_strat.iloc[2, :] = 0.0
        
        # Initial guesses for middle cards
        p1_strat.iloc[1, self.n-1] = 0.0  # Check probability with 5
        p1_strat.iloc[0, self.n-1] = 1.0  # Bet probability with 5
        
        p1_strat.iloc[1, self.n-2] = 0.0  # Check with 4
        p1_strat.iloc[0, self.n-2] = 1.0  # Bet with 4
        
        p1_strat.iloc[1, 2] = 0.49  # Check with 3
        p1_strat.iloc[0, 2] = 0.51  # Bet with 3
        
        p1_strat.iloc[1, 1] = 0.31  # Check with 2
        p1_strat.iloc[0, 1] = 0.69  # Bet with 2
        
        p1_strat.iloc[1, 0] = 1.0  # Check with 1 (bluff less initially)
        p1_strat.iloc[0, 0] = 0.0  # Don't always bet with 1
        
        # Call probabilities for middle cards
        p1_strat.iloc[4, 3] = 0.95  # Call with 4
        p1_strat.iloc[3, 3] = 0.05
        
        p1_strat.iloc[4, 2] = 0.49  # Call with 3
        p1_strat.iloc[3, 2] = 0.51
        
        p1_strat.iloc[4, 1] = 0.09  # Call with 2
        p1_strat.iloc[3, 1] = 0.91
        
        # Player 2 fixed strategies
        # Always bet/call with highest card
        p2_strat.iloc[1, self.n-1] = 1.0  # Bet with 5
        p2_strat.iloc[0, self.n-1] = 0.0  # Don't check with 5
        p2_strat.iloc[2, self.n-1] = 1.0  # Call with 5
        p2_strat.iloc[3, self.n-1] = 0.0  # Don't fold with 5
        
        # Always fold with lowest card
        p2_strat.iloc[2, 0] = 0.0  # Don't call with 1
        p2_strat.iloc[3, 0] = 1.0  # Fold with 1
        
        # Initial guesses
        p2_strat.iloc[1, 3] = 0.91  # Bet with 4
        p2_strat.iloc[0, 3] = 0.09  # Check with 4
        
        p2_strat.iloc[1, 2] = 0.61  # Bet with 3
        p2_strat.iloc[0, 2] = 0.39
        
        p2_strat.iloc[1, 1] = 0.21  # Bet with 2
        p2_strat.iloc[0, 1] = 0.79
        
        p2_strat.iloc[1, 0] = 0.81  # Bluff with 1
        p2_strat.iloc[0, 0] = 0.19
        
        # Call probabilities
        p2_strat.iloc[3, 3] = 0.11  # Fold with 4
        p2_strat.iloc[2, 3] = 0.89  # Call with 4
        
        p2_strat.iloc[3, 2] = 0.51  # Fold with 3
        p2_strat.iloc[2, 2] = 0.49  # Call with 3
        
        p2_strat.iloc[3, 1] = 0.79  # Fold with 2
        p2_strat.iloc[2, 1] = 0.21  # Call with 2
        
        return p1_strat, p2_strat


class EVCalculator:
    """
    Calculates expected value for each player given their strategies.
    """
    
    def __init__(self, engine: KuhnPokerEngine):
        """
        Initialize EV calculator.
        
        Args:
            engine: KuhnPokerEngine instance
        """
        self.engine = engine
        self.n = engine.n
        
    def calculate_ev(self, strategy_1: pd.DataFrame, 
                    strategy_2: pd.DataFrame) -> Tuple[float, float]:
        """
        Calculate expected value for both players given their strategies.
        
        Args:
            strategy_1: Player 1's strategy matrix
            strategy_2: Player 2's strategy matrix
            
        Returns:
            Tuple of (ev_player1, ev_player2)
        """
        ev_1 = 0.0
        ev_2 = 0.0
        
        # Iterate through all possible card combinations
        for hand_1 in range(1, self.n + 1):
            for hand_2 in range(1, self.n + 1):
                if hand_1 == hand_2:  # Can't have same card
                    continue
                
                # Probability of this hand combination
                prob_hands = 1.0 / (self.n * (self.n - 1))
                
                # Calculate EV for all action combinations
                hand_1_idx = hand_1 - 1
                hand_2_idx = hand_2 - 1
                
                # P1 bets (action_1a = 1)
                prob_1_bet = strategy_1.iloc[0, hand_1_idx]
                
                # P2 calls
                prob_2_call = strategy_2.iloc[2, hand_2_idx]
                prob_both_bet_call = prob_1_bet * prob_2_call
                if prob_both_bet_call > 0:
                    stack_1, stack_2 = self.engine.run_game(1, 0, 0, 2, hand_1, hand_2)
                    ev_1 += prob_hands * prob_both_bet_call * stack_1
                    ev_2 += prob_hands * prob_both_bet_call * stack_2
                
                # P2 folds
                prob_2_fold = strategy_2.iloc[3, hand_2_idx]
                prob_bet_fold = prob_1_bet * prob_2_fold
                if prob_bet_fold > 0:
                    stack_1, stack_2 = self.engine.run_game(1, 0, 0, 3, hand_1, hand_2)
                    ev_1 += prob_hands * prob_bet_fold * stack_1
                    ev_2 += prob_hands * prob_bet_fold * stack_2
                
                # P1 checks (action_1a = 2)
                prob_1_check = strategy_1.iloc[1, hand_1_idx]
                
                # P2 bets after P1 checks
                prob_2_bet = strategy_2.iloc[0, hand_2_idx]
                prob_check_bet = prob_1_check * prob_2_bet
                
                if prob_check_bet > 0:
                    # P1 calls
                    prob_1_call = strategy_1.iloc[4, hand_1_idx]
                    prob_check_bet_call = prob_check_bet * prob_1_call
                    if prob_check_bet_call > 0:
                        stack_1, stack_2 = self.engine.run_game(2, 2, 1, 0, hand_1, hand_2)
                        ev_1 += prob_hands * prob_check_bet_call * stack_1
                        ev_2 += prob_hands * prob_check_bet_call * stack_2
                    
                    # P1 folds
                    prob_1_fold = strategy_1.iloc[3, hand_1_idx]
                    prob_check_bet_fold = prob_check_bet * prob_1_fold
                    if prob_check_bet_fold > 0:
                        stack_1, stack_2 = self.engine.run_game(2, 3, 1, 0, hand_1, hand_2)
                        ev_1 += prob_hands * prob_check_bet_fold * stack_1
                        ev_2 += prob_hands * prob_check_bet_fold * stack_2
                
                # P2 checks after P1 checks
                prob_2_check = strategy_2.iloc[1, hand_2_idx]
                prob_both_check = prob_1_check * prob_2_check
                if prob_both_check > 0:
                    stack_1, stack_2 = self.engine.run_game(2, 0, 2, 0, hand_1, hand_2)
                    ev_1 += prob_hands * prob_both_check * stack_1
                    ev_2 += prob_hands * prob_both_check * stack_2
        
        return ev_1, ev_2


class ProbabilityUpdater:
    """
    Updates strategy probabilities using iterative improvement.
    """
    
    def __init__(self, ev_calculator: EVCalculator):
        """
        Initialize updater.
        
        Args:
            ev_calculator: EVCalculator instance
        """
        self.ev_calc = ev_calculator
        
    def update_probability(self, n: int, k: int, strategy_update: pd.DataFrame,
                          strategy_fixed: pd.DataFrame, row1: int, column: int,
                          row2: int, player: int, epsilon: float) -> Tuple[float, pd.DataFrame]:
        """
        Update a single probability in the strategy matrix.
        
        Args:
            n: Number of cards
            k: Maximum iterations
            strategy_update: Strategy matrix being updated
            strategy_fixed: Opponent's fixed strategy
            row1: First row to update
            column: Column (card) to update
            row2: Second row to update (complementary probability)
            player: 1 or 2
            epsilon: Update step size
            
        Returns:
            Tuple of (final_ev, updated_strategy)
        """
        strategy_update = strategy_update.copy()
        counter = 0
        
        for _ in range(k):
            # Calculate current EV
            if player == 1:
                ev_initial, _ = self.ev_calc.calculate_ev(strategy_update, strategy_fixed)
            else:
                _, ev_initial = self.ev_calc.calculate_ev(strategy_fixed, strategy_update)
            
            # Try increasing probability
            strategy_increase = strategy_update.copy()
            if strategy_increase.iloc[row1, column] + epsilon >= 1.0:
                strategy_increase.iloc[row1, column] = 1.0
                strategy_increase.iloc[row2, column] = 0.0
            else:
                strategy_increase.iloc[row1, column] += epsilon
                strategy_increase.iloc[row2, column] = 1.0 - strategy_increase.iloc[row1, column]
            
            # Try decreasing probability
            strategy_decrease = strategy_update.copy()
            if strategy_decrease.iloc[row1, column] - epsilon <= 0.0:
                strategy_decrease.iloc[row1, column] = 0.0
                strategy_decrease.iloc[row2, column] = 1.0
            else:
                strategy_decrease.iloc[row1, column] -= epsilon
                strategy_decrease.iloc[row2, column] = 1.0 - strategy_decrease.iloc[row1, column]
            
            # Calculate EVs for increased and decreased strategies
            if strategy_increase.iloc[row1, column] == strategy_update.iloc[row1, column] and \
               strategy_increase.iloc[row1, column] == 1.0:
                ev_increase = -9999
            else:
                if player == 1:
                    ev_increase, _ = self.ev_calc.calculate_ev(strategy_increase, strategy_fixed)
                else:
                    _, ev_increase = self.ev_calc.calculate_ev(strategy_fixed, strategy_increase)
            
            if strategy_decrease.iloc[row1, column] == strategy_update.iloc[row1, column] and \
               strategy_decrease.iloc[row1, column] == 0.0:
                ev_decrease = -9999
            else:
                if player == 1:
                    ev_decrease, _ = self.ev_calc.calculate_ev(strategy_decrease, strategy_fixed)
                else:
                    _, ev_decrease = self.ev_calc.calculate_ev(strategy_fixed, strategy_decrease)
            
            # Update strategy in direction of improvement
            if ev_increase > ev_decrease and ev_increase > ev_initial:
                strategy_update = strategy_increase
            elif ev_decrease > ev_increase and ev_decrease > ev_initial:
                strategy_update = strategy_decrease
            
            # Break if no improvement or reached max iterations
            if counter == k:
                break
            elif ev_initial >= ev_increase and ev_initial >= ev_decrease:
                break
            
            counter += 1
        
        return ev_initial, strategy_update


class EquilibriumSolver:
    """
    Main solver that uses self-play to find Nash equilibrium.
    """
    
    def __init__(self, n: int = 5):
        """
        Initialize solver.
        
        Args:
            n: Number of cards in deck
        """
        self.n = n
        self.engine = KuhnPokerEngine(n)
        self.ev_calc = EVCalculator(self.engine)
        self.updater = ProbabilityUpdater(self.ev_calc)
        self.strategy_mgr = StrategyManager(n)
        
    def solve(self, p1_start: pd.DataFrame, p2_start: pd.DataFrame,
             max_iterations: int = 10000, epsilon: float = 0.0001,
             check_frequency: int = 100) -> List[Dict[str, Any]]:
        """
        Run the equilibrium solver.
        
        Args:
            p1_start: Initial strategy for Player 1
            p2_start: Initial strategy for Player 2
            max_iterations: Maximum solver iterations
            epsilon: Update step size
            check_frequency: How often to check for equilibrium
            
        Returns:
            List of found equilibrium strategies
        """
        output_list = []
        p1_temp = p1_start.copy()
        p2_temp = p2_start.copy()
        
        print("Initial Strategies")
        print("\nPlayer 1:")
        print(p1_temp)
        print("\nPlayer 2:")
        print(p2_temp)
        
        counter = 1
        equilibria_found = 0
        
        while counter <= max_iterations:
            # Update Player 1 Stage 1 (first node probabilities)
            print(f"\n=== Iteration {counter} ===")
            print("Updating Player 1 Stage 1...")
            
            for hand in range(self.n):
                action = 0  # Bet/Check row
                # Skip certain fixed strategies
                if hand == 0 and action == 3:  # Don't update fold with card 1
                    continue
                elif hand == self.n - 1 and action == 3:  # Don't update fold with card 5
                    continue
                else:
                    alternate_row = action + 1
                    ev_1, p1_temp = self.updater.update_probability(
                        self.n, 1, p1_temp, p2_temp, action, hand, 
                        alternate_row, 1, epsilon
                    )
            
            # Update Player 2
            print("Updating Player 2...")
            for hand in range(4):  # Cards 1-4 (card 5 is fixed)
                for action in [0, 2]:  # Bet/Check and Call/Fold rows
                    if hand == 0 and action == 2:  # Don't update call with card 1
                        continue
                    else:
                        alternate_row = action + 1
                        ev_2, p2_temp = self.updater.update_probability(
                            self.n, 1, p2_temp, p1_temp, action, hand,
                            alternate_row, 2, epsilon
                        )
            
            # Update Player 1 Stage 3 (call/fold probabilities)
            print("Updating Player 1 Stage 3...")
            for hand in range(self.n):
                action = 3  # Fold row
                if hand == 0 and action == 3:  # Don't update fold with card 1
                    continue
                elif hand == self.n - 1 and action == 3:  # Don't update fold with card 5
                    continue
                else:
                    alternate_row = action + 1
                    ev_1, p1_temp = self.updater.update_probability(
                        self.n, 1, p1_temp, p2_temp, action, hand,
                        alternate_row, 1, epsilon
                    )
            
            # Check for equilibrium periodically
            if counter > 5000 or counter % check_frequency == 0:
                print(f"\nChecking for equilibrium at iteration {counter}...")
                ev_1, ev_2 = self.ev_calc.calculate_ev(p1_temp, p2_temp)
                print(f"Current EVs: P1={ev_1:.6f}, P2={ev_2:.6f}")
                
                is_equilibrium = self.check_equilibrium(p1_temp, p2_temp, ev_1, ev_2)
                
                if is_equilibrium:
                    print("\n*** EQUILIBRIUM FOUND ***")
                    print("\nPlayer 1 Strategy:")
                    print(p1_temp)
                    print("\nPlayer 2 Strategy:")
                    print(p2_temp)
                    print(f"\nEVs: P1={ev_1:.6f}, P2={ev_2:.6f}")
                    
                    output_list.append({
                        'iteration': counter,
                        'player1_strategy': p1_temp.copy(),
                        'player2_strategy': p2_temp.copy(),
                        'ev_player1': ev_1,
                        'ev_player2': ev_2
                    })
                    
                    equilibria_found += 1
                    if equilibria_found >= 3:  # Stop after finding 3 equilibria
                        break
            
            counter += 1
        
        return output_list
    
    def check_equilibrium(self, player1: pd.DataFrame, player2: pd.DataFrame,
                         ev_old_1: float, ev_old_2: float,
                         epsilon_threshold: float = 0.01) -> bool:
        """
        Check if current strategies form an epsilon-Nash equilibrium.
        
        Args:
            player1: Player 1's strategy
            player2: Player 2's strategy
            ev_old_1: Player 1's EV with current strategies
            ev_old_2: Player 2's EV with current strategies
            epsilon_threshold: Maximum exploitability allowed
            
        Returns:
            True if strategies form epsilon-equilibrium
        """
        # Find best response for Player 1
        p1_best_response = player1.copy()
        for hand in range(self.n):
            for action in [0, 3]:  # Bet/Check and Fold rows
                if hand == 0 and action == 3:
                    continue
                elif hand == self.n - 1 and action == 3:
                    continue
                else:
                    alternate_row = action + 1
                    _, p1_best_response = self.updater.update_probability(
                        self.n, 9999, p1_best_response, player2, action, hand,
                        alternate_row, 1, 0.01
                    )
        
        # Find best response for Player 2
        p2_best_response = player2.copy()
        for hand in range(4):
            for action in [0, 2]:
                if hand == 0 and action == 2:
                    continue
                else:
                    alternate_row = action + 1
                    _, p2_best_response = self.updater.update_probability(
                        self.n, 9999, p2_best_response, player1, action, hand,
                        alternate_row, 2, 0.01
                    )
        
        # Calculate EVs with best responses
        ev_1_br, _ = self.ev_calc.calculate_ev(p1_best_response, player2)
        _, ev_2_br = self.ev_calc.calculate_ev(player1, p2_best_response)
        
        # Check if exploitability is below threshold
        exploitability_1 = abs(ev_old_1 - ev_1_br)
        exploitability_2 = abs(ev_old_2 - ev_2_br)
        
        print(f"Exploitability: P1={exploitability_1:.6f}, P2={exploitability_2:.6f}")
        
        return exploitability_1 <= epsilon_threshold and exploitability_2 <= epsilon_threshold


def main():
    """
    Main function to run the solver.
    """
    print("5-Card Kuhn Poker Solver")
    print("=" * 50)
    
    # Initialize solver
    solver = EquilibriumSolver(n=5)
    
    # Get default starting strategies
    p1_start, p2_start = solver.strategy_mgr.initialize_default_strategy()
    
    # Run solver
    print("\nStarting solver...")
    results = solver.solve(
        p1_start, p2_start,
        max_iterations=10000,
        epsilon=0.0001,
        check_frequency=100
    )
    
    # Display results
    print("\n" + "=" * 50)
    print(f"Solver completed. Found {len(results)} equilibria.")
    
    if results:
        print("\nFinal equilibrium:")
        final = results[-1]
        print(f"\nIteration: {final['iteration']}")
        print(f"EVs: P1={final['ev_player1']:.6f}, P2={final['ev_player2']:.6f}")
        print("\nPlayer 1 Strategy:")
        print(final['player1_strategy'])
        print("\nPlayer 2 Strategy:")
        print(final['player2_strategy'])
    
    return results


if __name__ == "__main__":
    results = main()
