# ============================================================
# tictactoe.py
# ============================================================
"""
Tic Tac Toe board representation and search algorithms (BFS vs DFS).

Board representation: a list of 9 cells, indexed 0-8 left-to-right, top-to-bottom:

    0 | 1 | 2
    --+---+--
    3 | 4 | 5
    --+---+--
    6 | 7 | 8

Each cell holds 'X', 'O', or None (empty).

Both bfs_find_win() and dfs_find_win() search the game tree, alternating
moves between X and O, for the FIRST decisive (win) terminal state reached
by the search -- they are plain tree-search algorithms, not adversarial
(minimax) search. They both return (path_length, nodes_expanded, path).
"""

from collections import deque

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),   # columns
    (0, 4, 8), (2, 4, 6),              # diagonals
]


def get_empty_cells(board):
    """Return the list of empty cell indices, in ascending order."""
    return [i for i, v in enumerate(board) if v is None]


def make_move(board, cell, player):
    """Return a NEW board with `player`'s mark placed at `cell`."""
    new_board = board[:]
    new_board[cell] = player
    return new_board


def check_winner(board):
    """Return 'X' or 'O' if that player has three in a row, else None."""
    for a, b, c in WIN_LINES:
        if board[a] is not None and board[a] == board[b] == board[c]:
            return board[a]
    return None


def next_player_to_move(board):
    """X always moves first; whoever has fewer marks on the board moves next."""
    x_count = board.count('X')
    o_count = board.count('O')
    return 'X' if x_count <= o_count else 'O'


def bfs_find_win(board):
    """
    Breadth-first search for the first decisive (win) terminal state.

    Explores the tree level by level, so the first win found is guaranteed
    to be at the shallowest possible depth (fewest moves) -- BFS is
    complete and optimal in depth on this unweighted tree.

    Returns:
        (path_length, nodes_expanded, path)
        path is a list of (cell, player) moves from the given board to the
        winning state. Returns (None, nodes_expanded, None) if no decisive
        state is reachable (all lines lead to a draw).
    """
    start_player = next_player_to_move(board)
    frontier = deque()
    frontier.append((board, start_player, []))
    nodes_expanded = 0

    while frontier:
        current_board, player, path = frontier.popleft()
        nodes_expanded += 1

        winner = check_winner(current_board)
        if winner is not None:
            return len(path), nodes_expanded, path

        empties = get_empty_cells(current_board)
        if not empties:
            continue  # draw -- dead end, don't expand further

        for cell in empties:
            new_board = make_move(current_board, cell, player)
            new_path = path + [(cell, player)]
            next_player = 'O' if player == 'X' else 'X'
            frontier.append((new_board, next_player, new_path))

    return None, nodes_expanded, None


def dfs_find_win(board, depth_limit=9):
    """
    Depth-first search for the first decisive (win) terminal state,
    depth-limited to `depth_limit` plies (9 = the max length of a game).

    Cells are always tried in a FIXED ascending order (0 through 8), so
    DFS commits to filling cells left-to-right before ever reconsidering.
    This makes it cheap (few nodes expanded) but not optimal -- the path
    it finds is often longer than the shortest possible win.

    Returns the same shape as bfs_find_win(): (path_length, nodes_expanded, path).
    """
    start_player = next_player_to_move(board)
    stack = [(board, start_player, [])]
    nodes_expanded = 0

    while stack:
        current_board, player, path = stack.pop()
        nodes_expanded += 1

        winner = check_winner(current_board)
        if winner is not None:
            return len(path), nodes_expanded, path

        if len(path) >= depth_limit:
            continue  # hit the depth limit -- don't expand further

        empties = get_empty_cells(current_board)
        # Push in reverse order so pop() (LIFO) still visits cells 0..8 first.
        for cell in reversed(empties):
            new_board = make_move(current_board, cell, player)
            new_path = path + [(cell, player)]
            next_player = 'O' if player == 'X' else 'X'
            stack.append((new_board, next_player, new_path))

    return None, nodes_expanded, None


def print_board(board):
    """Pretty-print a board to the console, for quick sanity checks."""
    symbols = [c if c else str(i) for i, c in enumerate(board)]
    rows = [symbols[0:3], symbols[3:6], symbols[6:9]]
    lines = [" | ".join(row) for row in rows]
    print(("\n" + "-" * 9 + "\n").join(lines))


if __name__ == "__main__":
    # Quick manual sanity check
    endgame_board = ['X', 'X', None, 'O', 'O', None, None, None, None]
    print("Endgame board:")
    print_board(endgame_board)

    bfs_result = bfs_find_win(endgame_board)
    dfs_result = dfs_find_win(endgame_board)
    print("\nBFS:", bfs_result)
    print("DFS:", dfs_result)


# ============================================================
# run_experiments.py
# ============================================================
"""
Driver script for the BFS vs DFS Tic Tac Toe profiling experiments.

Runs both algorithms on three test boards (best / average / worst case),
5 runs per algorithm per test case (15 runs total per algorithm), timing
each run with time.perf_counter(). Writes results.json and prints a
summary table.

Usage:
    python run_experiments.py
"""

import json
import time

from tictactoe import bfs_find_win, dfs_find_win, print_board

RUNS_PER_CASE = 5

# Test boards, in increasing order of difficulty (fewer pre-filled cells
# = more of the tree left to search).
TEST_CASES = {
    "best_case_endgame": ['X', 'X', None, 'O', 'O', None, None, None, None],
    "average_case_midgame": ['X', None, None, None, 'O', None, None, None, 'X'],
    "worst_case_empty": [None] * 9,
}

ALGORITHMS = {
    "BFS": bfs_find_win,
    "DFS": dfs_find_win,
}


def time_algorithm(fn, board, runs=RUNS_PER_CASE):
    """Run `fn` on `board` `runs` times, return (avg_time_ms, path_length, nodes_expanded)."""
    times_ms = []
    path_length = nodes_expanded = None

    for _ in range(runs):
        start = time.perf_counter()
        path_length, nodes_expanded, _path = fn(board)
        elapsed_ms = (time.perf_counter() - start) * 1000
        times_ms.append(elapsed_ms)

    avg_time_ms = sum(times_ms) / len(times_ms)
    return avg_time_ms, path_length, nodes_expanded


def main():
    results = {}

    for case_name, board in TEST_CASES.items():
        print(f"\n=== {case_name} ===")
        print_board(board)
        results[case_name] = {}

        for algo_name, algo_fn in ALGORITHMS.items():
            avg_time_ms, path_length, nodes_expanded = time_algorithm(algo_fn, board)
            results[case_name][algo_name] = {
                "avg_time_ms": round(avg_time_ms, 4),
                "moves_to_decide": path_length,
                "nodes_expanded": nodes_expanded,
            }
            print(f"{algo_name}: avg_time={avg_time_ms:.4f} ms, "
                  f"moves_to_decide={path_length}, nodes_expanded={nodes_expanded}")

    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\nResults written to results.json")


if __name__ == "__main__":
    main()


# ============================================================
# generate_charts.py
# ============================================================
"""
Generates Fig. 3 -- Average execution time: BFS vs DFS across the three
test cases -- from results.json (produced by run_experiments.py).

Usage:
    python run_experiments.py     # first, to produce results.json
    python generate_charts.py     # then, to produce fig3_avg_time.png
"""

import json

import matplotlib.pyplot as plt
import numpy as np

with open("results.json") as f:
    results = json.load(f)

case_labels = list(results.keys())
bfs_times = [results[case]["BFS"]["avg_time_ms"] for case in case_labels]
dfs_times = [results[case]["DFS"]["avg_time_ms"] for case in case_labels]

x = np.arange(len(case_labels))
width = 0.35

fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(x - width / 2, bfs_times, width, label="BFS")
ax.bar(x + width / 2, dfs_times, width, label="DFS")

ax.set_ylabel("Average execution time (ms)")
ax.set_title("Fig. 3 - Average execution time: BFS vs DFS across the three test cases")
ax.set_xticks(x)
ax.set_xticklabels(case_labels, rotation=15, ha="right")
ax.legend()
fig.tight_layout()

fig.savefig("fig3_avg_time.png", dpi=150)
print("Saved fig3_avg_time.png")


# ============================================================
# profile_flamegraph.py
# ============================================================
"""
Generates Fig. 2 -- a flame graph of the BFS/DFS Tic Tac Toe driver run.

The intended tool was py-spy:

    py-spy record -o flamegraph.svg --rate 100 -- python run_experiments.py

py-spy's compiled binary could not be installed in the sandboxed, offline
environment used to prepare this report, so this script builds the same
kind of flame graph using Python's built-in cProfile module instead --
run against the exact same code -- which serves the same purpose
(showing where time is spent).

Requires the `flameprof` package to render an SVG (pip install flameprof).
If flameprof isn't available, this still writes a .prof file you can open
with `snakeviz profile_output.prof` or inspect with pstats.

Usage:
    python profile_flamegraph.py
"""

import cProfile
import pstats
import subprocess
import sys

from run_experiments import main as run_experiments_main

PROFILE_FILE = "profile_output.prof"
FLAMEGRAPH_SVG = "flamegraph.svg"


def profile_and_save():
    profiler = cProfile.Profile()
    profiler.enable()
    run_experiments_main()
    profiler.disable()
    profiler.dump_stats(PROFILE_FILE)
    print(f"\nSaved raw profile data to {PROFILE_FILE}")

    # Print the top time-consuming functions to the console as a quick check.
    stats = pstats.Stats(PROFILE_FILE)
    stats.sort_stats("cumulative")
    print("\nTop functions by cumulative time:")
    stats.print_stats(10)


def render_flamegraph():
    try:
        subprocess.run(
            [sys.executable, "-m", "flameprof", PROFILE_FILE, FLAMEGRAPH_SVG],
            check=True,
        )
        print(f"Saved flame graph to {FLAMEGRAPH_SVG}")
    except FileNotFoundError:
        print("flameprof not installed -- skipping SVG render. "
              "Install with: pip install flameprof")
    except subprocess.CalledProcessError as e:
        print(f"flameprof failed: {e}")


if __name__ == "__main__":
    profile_and_save()
    render_flamegraph()
