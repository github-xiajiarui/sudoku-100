#!/usr/bin/env python3
import json, sys

with open('levels.json') as f:
    L = json.load(f)
print(f'Total levels: {len(L)}')

def solve_sudoku(puzzle, max_solutions=2):
    grid = [row[:] for row in puzzle]
    solutions = []
    
    def is_valid(r, c, v):
        for i in range(9):
            if grid[r][i] == v or grid[i][c] == v:
                return False
        br, bc = (r//3)*3, (c//3)*3
        for i in range(3):
            for j in range(3):
                if grid[br+i][bc+j] == v:
                    return False
        return True
    
    def backtrack():
        if len(solutions) >= max_solutions:
            return
        for r in range(9):
            for c in range(9):
                if grid[r][c] == 0:
                    for v in range(1, 10):
                        if is_valid(r, c, v):
                            grid[r][c] = v
                            backtrack()
                            grid[r][c] = 0
                            if len(solutions) >= max_solutions:
                                return
                    return
        solutions.append([row[:] for row in grid])
    
    backtrack()
    return solutions

# Check level 28 first
print("\n=== Level 28 (index 27) ===")
lv = L[27]
sols = solve_sudoku(lv['p'])
print(f"Solutions: {len(sols)}")
for r in lv['p']:
    print(r)
print("---")
if sols:
    for r in sols[0]:
        print(r)

# Check all
print("\n=== All 100 levels ===")
bad = []
for i, lv in enumerate(L):
    sols = solve_sudoku(lv['p'])
    if len(sols) == 0:
        bad.append((i, 'NO SOLUTION'))
    elif len(sols) > 1:
        bad.append((i, f'{len(sols)} SOLUTIONS'))
    elif sols[0] != lv['s']:
        bad.append((i, 'MISMATCH'))

if not bad:
    print("All 100 unique ✓")
else:
    print(f"{len(bad)} bad levels:")
    for idx, reason in bad:
        print(f"  Level {idx+1} (idx {idx}): {reason}")
        if 'SOLUTIONS' in reason:
            lv = L[idx]
            sols = solve_sudoku(lv['p'])
            print("  Puzzle:")
            for r in lv['p']: print(f"    {r}")
            print("  Stored:")
            for r in lv['s']: print(f"    {r}")
            print("  Alt solution:")
            for r in sols[1]: print(f"    {r}")
