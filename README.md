# 5-Card Kuhn Poker Solver

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This is my attempt at solving 5-card Kuhn Poker for epsilon-Nash equilibrium (epsilon < 0.01) without using counterfactual regret minimization. Originally developed for my Master's thesis at University College Dublin (2018), cleaned up as a side project.

## Overview

Kuhn Poker is a simplified 2-player, zero-sum poker game originally developed with 3 cards by Harold Kuhn. This project extends the game to 5 cards and uses an iterative self-improvement algorithm to find epsilon-Nash equilibrium strategies.

The 3-card version has strict hand rankings (weak, medium, strong), so the equilibrium strategies are straightforward. With 5 cards, the middle cards (2, 3, 4) become ambiguous - they can serve as value bets, bluffs, or bluff-catchers depending on the opponent's strategy. This makes the strategy space more interesting and closer to real poker.

## Limitations

- The algorithm finds a single equilibrium and may not explore all equilibria
- Update order affects the convergence path
- No abstraction - only works for small games
- Slower than modern CFR-based solvers for larger games
- The 3-card game has infinite equilibria. I only found one here, and would like to eventually solve for more

## Quick Start

```bash
# Clone and install
git clone https://github.com/omermbashir/5-card-kuhn-poker.git
cd 5-card-kuhn-poker
pip install -r requirements.txt

# Run with my starting strategies (based on poker heuristics)
python kuhn_poker_solver.py

# Run with random starting strategies
python kuhn_poker_solver.py --random

# Run with random strategies using a specific seed (reproducible)
python kuhn_poker_solver.py --random 42

# Run tests
python test_solver.py

# See all options
python kuhn_poker_solver.py --help
```

### Using as a library

```python
from kuhn_poker_solver import EquilibriumSolver

solver = EquilibriumSolver(n=5)

# Heuristic starting strategies (recommended)
p1_start, p2_start = solver.strategy_mgr.initialize_default_strategy()

# Or random starting strategies
# p1_start, p2_start = solver.strategy_mgr.initialize_random_strategy(seed=42)

results = solver.solve(
    p1_start, p2_start,
    max_iterations=10000,
    epsilon=0.0001,
    check_frequency=100
)

if results:
    final = results[-1]
    print(f"Found equilibrium at iteration {final['iteration']}")
    print(f"Player 1 EV: {final['ev_player1']:.6f}")
    print(f"Player 2 EV: {final['ev_player2']:.6f}")
```

See `custom_solver.py` for a full example with custom starting strategies and result interpretation.

## Game Rules

Two players are each dealt one card from a deck of 5 (numbered 1-5). Both ante 1 unit.

1. **Player 1** acts first: bet (1 unit) or check
2. If Player 1 bets: Player 2 can call or fold
3. If Player 1 checks: Player 2 can bet or check
4. If Player 2 bets after a check: Player 1 can call or fold
5. Any showdown is won by the higher card

## Algorithm

The solver uses iterative self-improvement through local search:

1. Initialize both players with starting strategies
2. For each card and action, try small probability adjustments and keep changes that improve expected value
3. Update in a fixed order: Player 1 bet/check, then Player 2 bet/check and call/fold, then Player 1 call/fold
4. Periodically calculate best-response strategies and check if exploitability is below the threshold (epsilon < 0.01)
5. Stop when equilibrium is found or max iterations reached

The algorithm typically converges within 5,000-10,000 iterations.

### Components

- **KuhnPokerEngine** - game simulation and payoff calculation
- **EVCalculator** - expected value computation across all card combinations
- **ProbabilityUpdater** - local search over strategy probabilities
- **EquilibriumSolver** - orchestrates the self-play loop and convergence checking

## Results

After around 5,000 iterations, the solver converges to these equilibrium strategies:

### Player 1

| Card | Bet % | Check % | Call % | Fold % |
|------|-------|---------|--------|--------|
| 1 (worst) | 66% | 34% | 0% | 100% |
| 2 | 100% | 0% | 13% | 87% |
| 3 | 100% | 0% | 87% | 13% |
| 4 | 44% | 56% | 100% | 0% |
| 5 (best) | 46% | 54% | 100% | 0% |

Player 1 bluffs with card 1 about two-thirds of the time, value bets with middle cards, and mixes between betting and checking with strong cards (4-5) to stay unpredictable. Only calls with decent hands (3+).

### Player 2

| Card | Bet % (after check) | Check % | Call % (if bet) | Fold % |
|------|---------------------|---------|-----------------|--------|
| 1 (worst) | 24% | 76% | 0% | 100% |
| 2 | 100% | 0% | 14% | 86% |
| 3 | 100% | 0% | 63% | 37% |
| 4 | 0% | 100% | 100% | 0% |
| 5 (best) | 0% | 100% | 100% | 0% |

Player 2 occasionally bluffs with card 1 (24%) and aggressively bets middle cards. With strong cards (4-5), Player 2 checks to trap, then always calls if Player 1 bets.

### Sample output

```
=== Iteration 5247 ===
Checking for equilibrium at iteration 5247...
Current EVs: P1=-0.0316, P2=0.0316
Exploitability: P1=0.0098, P2=0.0095

*** EQUILIBRIUM FOUND ***

Player 1 Strategy:
            Card_1  Card_2  Card_3  Card_4  Card_5
P(Check 1)   0.336   0.000   0.000   0.561   0.543
P(Bet)       0.664   1.000   1.000   0.439   0.457
P(Fold 1)    0.000   0.000   0.000   0.000   0.000
P(Fold 2)    1.000   0.871   0.134   0.000   0.000
P(Call)      0.000   0.129   0.866   1.000   1.000

Player 2 Strategy:
               Card_1  Card_2  Card_3  Card_4  Card_5
P(Bet/Check)    0.244   1.000   1.000   0.000   0.000
P(Check/Fold)   0.756   0.000   0.000   1.000   1.000
P(Call)         0.000   0.126   0.640   1.000   1.000
P(Fold)         1.000   0.874   0.360   0.000   0.000

EVs: P1=-0.0316, P2=0.0316
Exploitability: < 0.01
```

## Theory

### Nash Equilibrium

A Nash equilibrium is a strategy profile where no player can improve their payoff by changing strategy. In 2-player zero-sum games, this is the optimal strategy - neither player can be exploited.

### Epsilon-Nash Equilibrium

An epsilon-Nash equilibrium is an approximation where no player can gain more than epsilon by deviating. Here, epsilon = 0.01 units per hand, meaning the strategy is exploitable by less than 1 cent per dollar of pot.

## Project Structure

```
kuhn_poker_solver.py    # Main solver
custom_solver.py        # Example with custom starting strategies
test_solver.py          # Automated tests
kuhn_poker_demo.ipynb   # Jupyter notebook demo
requirements.txt        # numpy, pandas
LICENSE                 # MIT
```

## References

- Kuhn, H. W. (1950). "Simplified Two-Person Poker". Contributions to the Theory of Games
- Bowling et al. (2015). "Heads-up limit hold'em poker is solved". Science
- Brown & Sandholm (2017). "Superhuman AI for heads-up no-limit poker: Libratus beats top professionals"

## Thesis

Based on my Master's thesis: "Epsilon Equilibrium in 5-Card Kuhn Poker" (2018). This was a throwback project I cleaned up in my free time.
