# Contribution Log

**Project:** Tic Tac Toe — BFS vs DFS Search Profiling (SLE-2, 02AML204)
**Author:** Shreyas Prakash More (PRN 25UAM071)

## My Contribution

- Decided on the board states and difficulty levels used for the best/average/worst-case comparison
- Actually ran the experiments
- Went through the numbers in `results.json`
- Checked that the flame graph output made sense
- Wrote the justification and conclusion based on the actual findings, not just theory

## AI Contribution (Claude, Anthropic)

- Helped write and structure the BFS/DFS Tic Tac Toe code (`get_empty_cells()`, `make_move()`, `check_winner()`, `bfs_find_win()`, `dfs_find_win()`)
- Helped build the profiling/driver scripts
- Set up a `cProfile`-based flame graph as a stand-in for `py-spy` in the sandboxed, offline preparation environment, plus the exact `py-spy` command to reproduce it on a normal machine
- Drafted the chart/figure generation scripts (Fig. 1–3)
- Helped lay out this report in the required template format

## Summary

AI assistance covered code scaffolding, tooling setup, and document formatting. Experimental design, execution, result verification, and analytical conclusions were the author's own work.
