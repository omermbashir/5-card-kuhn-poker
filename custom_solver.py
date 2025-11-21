"""
Example: Custom Solver Run with Different Starting Strategies

This script demonstrates how to run the 5-card Kuhn Poker solver
with custom starting strategies.
"""

import sys
sys.path.append('..')

from kuhn_poker_solver import EquilibriumSolver
import pandas as pd


def run_custom_solver():
    """
    Run solver with a custom starting strategy.
    """
    print("5-Card Kuhn Poker - Custom Solver Example")
    print("=" * 60)
    
    # Initialize solver
    solver = EquilibriumSolver(n=5)
    
    # Get base strategy matrices
    p1_custom, p2_custom = solver.strategy_mgr.create_strategy_matrix()
    
    # Define custom starting strategies
    # These are strategies from the thesis that converged well
    
    # Player 1 custom strategy
    # Row 0: P(Check with card), Row 1: P(Bet with card)
    # Row 2: P(Fold1), Row 3: P(Fold2), Row 4: P(Call)
    
    # Card 1 (worst card)
    p1_custom.iloc[0, 0] = 0.664  # Check
    p1_custom.iloc[1, 0] = 0.336  # Bet (bluff sometimes)
    p1_custom.iloc[2, 0] = 0.0    # No fold in first node
    p1_custom.iloc[3, 0] = 1.0    # Always fold to bet
    p1_custom.iloc[4, 0] = 0.0    # Never call with 1
    
    # Card 2
    p1_custom.iloc[0, 1] = 0.0
    p1_custom.iloc[1, 1] = 1.0
    p1_custom.iloc[2, 1] = 0.0
    p1_custom.iloc[3, 1] = 0.871
    p1_custom.iloc[4, 1] = 0.129
    
    # Card 3
    p1_custom.iloc[0, 2] = 0.0
    p1_custom.iloc[1, 2] = 1.0
    p1_custom.iloc[2, 2] = 0.0
    p1_custom.iloc[3, 2] = 0.134
    p1_custom.iloc[4, 2] = 0.866
    
    # Card 4
    p1_custom.iloc[0, 3] = 0.439
    p1_custom.iloc[1, 3] = 0.561
    p1_custom.iloc[2, 3] = 0.0
    p1_custom.iloc[3, 3] = 0.0
    p1_custom.iloc[4, 3] = 1.0
    
    # Card 5 (best card)
    p1_custom.iloc[0, 4] = 0.457
    p1_custom.iloc[1, 4] = 0.543
    p1_custom.iloc[2, 4] = 0.0
    p1_custom.iloc[3, 4] = 0.0
    p1_custom.iloc[4, 4] = 1.0
    
    # Player 2 custom strategy
    # Row 0: P(Bet/Check in left node), Row 1: P(Check/Fold in left node)
    # Row 2: P(Call in right node), Row 3: P(Fold in right node)
    
    # Card 1
    p2_custom.iloc[0, 0] = 0.244
    p2_custom.iloc[1, 0] = 0.756
    p2_custom.iloc[2, 0] = 0.0
    p2_custom.iloc[3, 0] = 1.0
    
    # Card 2
    p2_custom.iloc[0, 1] = 1.0
    p2_custom.iloc[1, 1] = 0.0
    p2_custom.iloc[2, 1] = 0.126
    p2_custom.iloc[3, 1] = 0.874
    
    # Card 3
    p2_custom.iloc[0, 2] = 1.0
    p2_custom.iloc[1, 2] = 0.0
    p2_custom.iloc[2, 2] = 0.64
    p2_custom.iloc[3, 2] = 0.36
    
    # Card 4
    p2_custom.iloc[0, 3] = 0.0
    p2_custom.iloc[1, 3] = 1.0
    p2_custom.iloc[2, 3] = 1.0
    p2_custom.iloc[3, 3] = 0.0
    
    # Card 5
    p2_custom.iloc[0, 4] = 0.0
    p2_custom.iloc[1, 4] = 1.0
    p2_custom.iloc[2, 4] = 1.0
    p2_custom.iloc[3, 4] = 0.0
    
    print("\nStarting Strategies:")
    print("\nPlayer 1:")
    print(p1_custom)
    print("\nPlayer 2:")
    print(p2_custom)
    
    # Run solver with custom strategies
    print("\n" + "=" * 60)
    print("Running solver...")
    print("=" * 60)
    
    results = solver.solve(
        p1_custom, p2_custom,
        max_iterations=5000,  # Fewer iterations for example
        epsilon=0.0001,
        check_frequency=100
    )
    
    # Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    if results:
        print(f"\nFound {len(results)} equilibrium/equilibria\n")
        
        for i, result in enumerate(results):
            print(f"\nEquilibrium #{i+1}:")
            print(f"  Iteration: {result['iteration']}")
            print(f"  Player 1 EV: {result['ev_player1']:.6f}")
            print(f"  Player 2 EV: {result['ev_player2']:.6f}")
        
        # Show final equilibrium in detail
        print("\n" + "=" * 60)
        print("FINAL EQUILIBRIUM STRATEGIES")
        print("=" * 60)
        
        final = results[-1]
        print("\nPlayer 1 Strategy:")
        print(final['player1_strategy'].round(4))
        print("\nPlayer 2 Strategy:")
        print(final['player2_strategy'].round(4))
        
        print("\n" + "=" * 60)
        print("INTERPRETATION")
        print("=" * 60)
        
        print("\nPlayer 1 with card 3 (middle card):")
        p1_card3 = final['player1_strategy'].iloc[:, 2]
        print(f"  Bets {p1_card3[0]*100:.1f}% of the time")
        print(f"  Checks {p1_card3[1]*100:.1f}% of the time")
        print(f"  When facing a bet: calls {p1_card3[4]*100:.1f}%, folds {p1_card3[3]*100:.1f}%")
        
        print("\nPlayer 2 with card 3 (middle card):")
        p2_card3 = final['player2_strategy'].iloc[:, 2]
        print(f"  After P1 checks: bets {p2_card3[0]*100:.1f}%, checks {p2_card3[1]*100:.1f}%")
        print(f"  After P1 bets: calls {p2_card3[2]*100:.1f}%, folds {p2_card3[3]*100:.1f}%")
        
        print("\n" + "=" * 60)
    else:
        print("\nNo equilibrium found within iteration limit.")
        print("Try increasing max_iterations or adjusting starting strategies.")
    
    return results


def compare_strategies():
    """
    Compare different starting strategies and their convergence.
    """
    print("\n" + "=" * 60)
    print("Comparing Different Starting Strategies")
    print("=" * 60)
    
    solver = EquilibriumSolver(n=5)
    
    # Strategy 1: Default
    print("\n\n### Running with default strategy...")
    p1_default, p2_default = solver.strategy_mgr.initialize_default_strategy()
    results_default = solver.solve(
        p1_default, p2_default,
        max_iterations=1000,
        check_frequency=500
    )
    
    # Strategy 2: More aggressive
    print("\n\n### Running with aggressive strategy...")
    p1_aggressive, p2_aggressive = solver.strategy_mgr.initialize_default_strategy()
    # Increase betting frequencies
    for card in range(5):
        if card > 0:  # Don't change card 1
            p1_aggressive.iloc[0, card] = min(1.0, p1_aggressive.iloc[0, card] + 0.2)
            p1_aggressive.iloc[1, card] = 1.0 - p1_aggressive.iloc[0, card]
    
    results_aggressive = solver.solve(
        p1_aggressive, p2_aggressive,
        max_iterations=1000,
        check_frequency=500
    )
    
    # Compare final EVs
    print("\n\n" + "=" * 60)
    print("COMPARISON RESULTS")
    print("=" * 60)
    
    if results_default:
        final_default = results_default[-1]
        print(f"\nDefault Strategy:")
        print(f"  Iterations to converge: {final_default['iteration']}")
        print(f"  Player 1 EV: {final_default['ev_player1']:.6f}")
        print(f"  Player 2 EV: {final_default['ev_player2']:.6f}")
    
    if results_aggressive:
        final_aggressive = results_aggressive[-1]
        print(f"\nAggressive Strategy:")
        print(f"  Iterations to converge: {final_aggressive['iteration']}")
        print(f"  Player 1 EV: {final_aggressive['ev_player1']:.6f}")
        print(f"  Player 2 EV: {final_aggressive['ev_player2']:.6f}")
    
    print("\nNote: Different starting strategies should converge to")
    print("similar equilibrium EVs, though the exact strategies may vary")
    print("if multiple equilibria exist.")


if __name__ == "__main__":
    # Run custom solver
    results = run_custom_solver()
    
    # Uncomment to compare different starting strategies
    # compare_strategies()
