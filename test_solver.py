"""
Quick test to verify the solver works correctly.
"""

from kuhn_poker_solver import EquilibriumSolver

def test_basic_functionality():
    """Test basic solver functionality."""
    print("Testing 5-Card Kuhn Poker Solver...")
    print("=" * 50)
    
    # Initialize solver
    solver = EquilibriumSolver(n=5)
    print("✓ Solver initialized")
    
    # Test strategy matrix creation
    p1, p2 = solver.strategy_mgr.create_strategy_matrix()
    assert p1.shape == (5, 5), "Player 1 strategy shape incorrect"
    assert p2.shape == (4, 5), "Player 2 strategy shape incorrect"
    print("✓ Strategy matrices created correctly")
    
    # Test default strategy initialization
    p1_start, p2_start = solver.strategy_mgr.initialize_default_strategy()
    assert p1_start.iloc[4, 4] == 1.0, "Player 1 should always call with card 5"
    assert p2_start.iloc[3, 0] == 1.0, "Player 2 should always fold with card 1"
    print("✓ Default strategies initialized correctly")
    
    # Test EV calculation
    ev1, ev2 = solver.ev_calc.calculate_ev(p1_start, p2_start)
    assert isinstance(ev1, float), "EV should be float"
    assert isinstance(ev2, float), "EV should be float"
    assert abs(ev1 + ev2) < 0.01, "EVs should sum to ~0 (zero-sum game)"
    print(f"✓ EV calculation works (P1: {ev1:.4f}, P2: {ev2:.4f})")
    
    # Test game engine
    stack1, stack2 = solver.engine.run_game(1, 0, 0, 2, 5, 1)  # P1 bets with 5, P2 calls with 1
    assert stack1 == 2.0, "P1 should win 2 units (pot of 4 minus 2 invested)"
    assert stack2 == -2.0, "P2 should lose 2 units"
    assert stack1 + stack2 == 0, "Zero-sum game"
    print("✓ Game engine works correctly")
    
    # Test small solver run
    print("\nRunning mini solver test (100 iterations)...")
    results = solver.solve(
        p1_start, p2_start,
        max_iterations=100,
        epsilon=0.001,
        check_frequency=50
    )
    print(f"✓ Solver ran for 100 iterations")
    
    print("\n" + "=" * 50)
    print("All tests passed! ✓")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    test_basic_functionality()
