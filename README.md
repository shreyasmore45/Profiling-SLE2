# Profiling-SLE2
# Tic Tac Toe — BFS vs DFS Search Profiling

**Course:** 02AML204 — Introduction to Artificial Intelligence
**Student:** Shreyas Prakash More (PRN 25UAM071), Division B
**Assignment:** SLE-2 Profiling Report

## Overview

This project compares two uninformed search strategies — **Breadth-First Search (BFS)** and **Depth-First Search (DFS)**, depth-limited to 9 plies — on the Tic Tac Toe game tree. Both algorithms search from a given board for the first decisive (win) terminal state, alternating moves between X and O, and return `(path_length, nodes_expanded, path)` so they can be compared on equal footing.

## Algorithms

- **Algorithm A — BFS:** explores the game tree level by level; guaranteed to find the state with the fewest moves (optimal), but expands many nodes as the board empties out.
- **Algorithm B — DFS:** explores depth-first with cells tried in a fixed ascending order (0–8), depth-limited to 9; much cheaper in nodes/time but not guaranteed to find the shortest path to a win.

## Repository Contents

- `run_experiments.py` — driver script that runs BFS/DFS on the three test boards and records timing/node counts
- `results.json` — raw timing and node-count data from the experiment runs
- `flamegraph.svg` / profiling output — call-graph showing where time is spent
- Report figures (`Fig. 1`–`Fig. 3`) — start/terminal board state, average execution time chart, and flame graph

## Methodology

- **Timing:** `time.perf_counter()`, 5 runs per algorithm per test case (15 runs total per algorithm)
- **Profiling:** intended tool was `py-spy` (`py-spy record -o flamegraph.svg --rate 100 -- python run_experiments.py`); since py-spy's compiled binary could not be installed in this sandboxed, offline environment, the flame graph was generated with Python's built-in `cProfile` against the same code instead
- **Test cases:** an endgame board (one move from a win), a midgame board (3 cells filled), and the empty starting board — covering best, average, and worst-case behaviour
- **Nodes expanded:** counted as board states popped off the frontier (queue for BFS, stack for DFS)

## Results Summary

| Metric | BFS | DFS | Better? |
|---|---|---|---|
| Best-case time (ms) | 0.0088 | 0.0148 | BFS |
| Average-case time (ms) | 0.1763 | 0.0182 | DFS |
| Worst-case time (ms) | 4.2386 | 0.0328 | DFS (fewer nodes) |
| Nodes expanded (avg. of 3 cases) | 393.7 | 6.3 | DFS (fewer expansions) |
| Solution optimal (fewest moves)? | Yes | No (up to 4 moves longer) | BFS |

## Key Finding

BFS always finds the fastest possible win (1, 3, 5 moves across the three boards) but its cost explodes as the board empties (2 → 56 → 1,123 nodes expanded), since it must fully clear every shallower ply before reaching the first decisive state. DFS stays cheap throughout (single-digit node counts, sub-0.1 ms) because its fixed left-to-right cell order happens to align with two of Tic Tac Toe's win lines — a coincidence of ordering, not a general advantage — but it takes 3–4 moves longer than necessary every time.

**Takeaway:** BFS should be the default choice whenever the speed of the outcome (fewest moves) matters; a cheap DFS result should not be trusted as "good enough" without checking how many moves it actually took.

## Complexity

- **BFS:** O(b^d) time and space, where *b* is the branching factor (up to 9, shrinking each ply) and *d* is the depth of the first decisive state
- **DFS:** O(b^m), where *m* is the depth limit (9); actual cost depends more on fixed cell-trial order than on proximity to a win

## Scaling Note

On a larger board (e.g. 4×4/5×5 connect-four style) with a bigger branching factor, BFS would eventually hit memory limits (O(b^d) space), while DFS's O(m) stack memory would hold up — but DFS would need a heuristic (e.g. Minimax with alpha-beta pruning) to reliably find *good*, fast wins rather than just any win.

## Reproducing the Flame Graph

​```bash
py-spy record -o flamegraph.svg --rate 100 -- python run_experiments.py
​```

*SLE-2 Student Guideline — Keep it simple, measure it, justify it.*
