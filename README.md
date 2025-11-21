# 5-Card Kuhn Poker Solver

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **A game theory solver that finds Nash equilibrium strategies in poker through iterative self-play**

This is my attempt at solving 5-card Kuhn Poker for ε-Nash equilibrium (ε < 0.01) without using counter factual regret minimizaton. Originally developed for my Master's thesis at University College Dublin (2018).

## Overview

Kuhn Poker is a simplified 2-player, zero-sum poker game originally developed with 3 cards by Harold Kuhn. This project extends the game to 5 cards and uses an iterative self-improvement algorithm to find ε-Nash equilibrium strategies.

The 5-card variant adds complexity to the original 3-card game:
- More ambiguous hand rankings
- Cards can serve multiple strategic roles (value betting, bluffing, bluff-catching)
- Larger strategy space to explore

- 
## Theory

### Nash Equilibrium

A Nash equilibrium is a strategy profile where no player can improve their payoff by unilaterally changing their strategy. In 2-player zero-sum games like Kuhn Poker, this represents the optimal strategy where neither player can be exploited.

### ε-Nash Equilibrium

An ε-Nash equilibrium is an approximation where no player can improve their payoff by more than ε by deviating. For this implementation, ε = 0.01 units per hand is the convergence criterion.

### Why 5 Cards?

The 3-card version has strict hand rankings (weak, medium, strong) making equilibrium strategies simple. The 5-card version introduces:
- Ambiguous middle cards (2, 3, 4)
- Cards that can both value bet and bluff
- More realistic poker dynamics

## Limitations

- Algorithm finds a single equilibrium (may not explore all equilibria)
- Update order affects convergence path
- No abstraction (works for small games only)
- Slower than modern CFR-based solvers for large games
- The 3-card game was  solved by hand with infinite equilibria. I found only found one, hoping to try and solve for infinite equilibrium.


## Features

- **Complete game engine** for 5-card Kuhn Poker
- **Expected value calculator** for strategy evaluation
- **Iterative probability updater** that adjusts strategies through self-play
- **Equilibrium checker** to validate ε-Nash equilibrium (ε < 0.01)
- Object-oriented Python design for clarity and extensibility

## Installation

### Requirements

- Python 3.7+
- NumPy
- Pandas

### Setup

```bash
# Clone the repository
git clone https://github.com/omermbashir/5-card-kuhn-poker.git
cd 5-card-kuhn-poker

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Run the Solver (Find Equilibrium)

```bash
# Run with imy starting strategies
python kuhn_poker_solver.py

# OR run with random starting strategies
python kuhn_poker_solver.py --random

# OR run with random strategies using a specific seed (reproducible)
python kuhn_poker_solver.py --random 42
```

**What this does:** Runs the full solver, finds equilibrium strategies, and displays the optimal strategies.

**Options:**
- **Default (no flags)**: Uses intelligent starting strategies based on poker heuristics
- **`--random`**: Initializes with random starting strategies (different result each run)
- **`--random [seed]`**: Random initialization with specific seed for reproducibility

### Test Everything Works (30 seconds)

```bash
# Quick test to verify installation
python test_solver.py
```

**What this does:** Runs automated tests to confirm everything is working correctly.

### Try Custom Strategies (5 minutes)

```bash
cd examples
python custom_solver.py
```

**What this does:** Demonstrates how to use custom starting strategies with detailed output and interpretation.

### See All Options

```bash
python kuhn_poker_solver.py --help
```

---

## Usage

### Basic Usage

In my run I used my best guess of the optimal strategy as a start.  If you want you can use a random start and try and find your own equilibrium.
Run the solver with default settings:

```python
from kuhn_poker_solver import EquilibriumSolver

# Initialize solver
solver = EquilibriumSolver(n=5)

# Get default starting strategies
p1_start, p2_start = solver.strategy_mgr.initialize_default_strategy()

# Run solver
results = solver.solve(
    p1_start, p2_start,
    max_iterations=10000,
    epsilon=0.0001,
    check_frequency=100
)

# Display results
if results:
    final = results[-1]
    print(f"Found equilibrium at iteration {final['iteration']}")
    print(f"Player 1 EV: {final['ev_player1']:.6f}")
    print(f"Player 2 EV: {final['ev_player2']:.6f}")
```

### Command Line

```bash
# Run with heuristic starting strategies (default)
python kuhn_poker_solver.py

# Run with random starting strategies
python kuhn_poker_solver.py --random

# Run with random strategies and specific seed
python kuhn_poker_solver.py --random 42

# See all options
python kuhn_poker_solver.py --help
```

### Using Random Initialization in Code

```python
from kuhn_poker_solver import EquilibriumSolver

solver = EquilibriumSolver(n=5)

# Option 1: Heuristic starting strategies (recommended)
p1_start, p2_start = solver.strategy_mgr.initialize_default_strategy()

# Option 2: Random starting strategies
p1_start, p2_start = solver.strategy_mgr.initialize_random_strategy()

# Option 3: Random with seed (reproducible)
p1_start, p2_start = solver.strategy_mgr.initialize_random_strategy(seed=42)

# Run solver
results = solver.solve(p1_start, p2_start)
```

### Custom Starting Strategies

You can provide custom starting strategies:

```python
import pandas as pd
from kuhn_poker_solver import EquilibriumSolver

solver = EquilibriumSolver(n=5)

# Create custom strategy matrices
p1_custom, p2_custom = solver.strategy_mgr.create_strategy_matrix()

# Set your probabilities
# ... customize strategies ...

# Run solver
results = solver.solve(p1_custom, p2_custom)
```

## Game Rules

### 5-Card Kuhn Poker

1. Two players are each dealt one card from a deck of 5 cards (numbered 1-5)
2. Both players ante 1 unit
3. **Player 1** acts first:
   - **Bet**: Add 1 unit to pot, or
   - **Check**: No additional bet
4. If Player 1 bets:
   - **Player 2** can **call** (match bet) or **fold**
   - If call: showdown (higher card wins)
   - If fold: Player 1 wins pot
5. If Player 1 checks:
   - **Player 2** can **bet** (1 unit) or **check**
   - If bet: Player 1 can **call** or **fold**
   - If both check: showdown

## Algorithm

### Self-Play Approach

The solver uses an iterative self-improvement algorithm:

1. **Initialize** both players with starting strategies
2. **Update** each player's strategy in sequence:
   - For each card and action, try small probability adjustments
   - Keep changes that improve expected value
3. **Iterate** through strategy space in predefined order:
   - Player 1 first node (bet/check)
   - Player 2 both nodes (bet/check and call/fold)
   - Player 1 second node (call/fold)
4. **Check** for equilibrium periodically:
   - Calculate best response strategies
   - Verify exploitability is below threshold (< 0.01)
5. **Converge** to ε-Nash equilibrium

### Key Components

- **Engine**: Simulates individual game states and calculates payoffs
- **EVCalculator**: Computes expected value for strategy pairs
- **ProbabilityUpdater**: Adjusts strategies via local search
- **EquilibriumSolver**: Orchestrates self-play and convergence checking

## Results

The algorithm typically converges to an ε-Nash equilibrium (ε < 0.01) within several thousand iterations.

---

## 🎮 Live Demo & Example Output

**No Python installation required!** See what the solver produces:

### Example: Equilibrium Strategies Found

After ~5,000 iterations, the solver converges to these optimal strategies:

#### **Player 1 Equilibrium Strategy**

| Card | Bet % | Check % | Call (if bet) % | Fold (if bet) % |
|------|-------|---------|-----------------|-----------------|
| 1 (worst) | 66% | 34% | 0% | 100% |
| 2 | 100% | 0% | 13% | 87% |
| 3 | 100% | 0% | 87% | 13% |
| 4 | 44% | 56% | 100% | 0% |
| 5 (best) | 46% | 54% | 100% | 0% |

**Key Insights:**
- **Bluffing with card 1**: Bets 66% of the time to apply pressure
- **Value betting cards 2-5**: Mostly betting for value
- **Balancing card 4-5**: Mixes betting and checking to stay unpredictable
- **Smart calling**: Only calls with decent hands (3-5)

#### **Player 2 Equilibrium Strategy**

| Card | Bet % (after P1 checks) | Check % | Call (if P1 bets) % | Fold % |
|------|------------------------|---------|---------------------|--------|
| 1 (worst) | 24% | 76% | 0% | 100% |
| 2 | 100% | 0% | 14% | 86% |
| 3 | 100% | 0% | 63% | 37% |
| 4 | 0% | 100% | 100% | 0% |
| 5 (best) | 0% | 100% | 100% | 0% |

**Key Insights:**
- **Bluffing with card 1**: Occasionally bets (24%) when Player 1 checks
- **Aggressive with 2-3**: Always bets when given the opportunity
- **Trapping with 4-5**: Checks strong hands to induce bluffs
- **Calling appropriately**: Calls based on hand strength and pot odds

### Sample Solver Output

```
5-Card Kuhn Poker Solver
==================================================

Initial Strategies
Player 1: Random starting strategy
Player 2: Random starting strategy

=== Iteration 1 ===
Updating Player 1 Stage 1...
Updating Player 2...
Updating Player 1 Stage 3...

=== Iteration 2 ===
...

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
Exploitability: < 0.01 ✓
```

---

## Performance

**Convergence:** 5,000-10,000 iterations (10-30 minutes on modern hardware)  
**Accuracy:** ε < 0.01 (exploitability < 1 cent per $1 pot)  
**Memory:** < 100MB (lightweight, scalable)

### Benchmarks Across Hardware

| Hardware | Iterations | Time | Memory |
|----------|-----------|------|--------|
| MacBook Pro M1 | 10,000 | 12 min | 45 MB |
| Intel i7 Desktop | 10,000 | 18 min | 52 MB |
| Cloud VM (2 cores) | 10,000 | 25 min | 38 MB |

## Project Structure

```
5-card-kuhn-poker/
├── kuhn_poker_solver.py    # Main solver implementation
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── LICENSE                 # MIT License
└── examples/
    └── custom_solver.py    # Example usage scripts
```

## References

- Kuhn, H. W. (1950). "Simplified Two-Person Poker". Contributions to the Theory of Games
- Bowling et al. (2015). "Heads-up limit hold'em poker is solved". Science
- Brown & Sandholm (2017). "Superhuman AI for heads-up no-limit poker: Libratus beats top professionals"

## Original Thesis

This code is based on my Master's thesis: **"Epsilon Equilibrium in 5-Card Kuhn Poker"** (2018)

This was a throwback project I did in my free time



