#!/usr/bin/env python3
"""
Ultra-fast unique-solution generator.
Strategy: generate complete boards and use a heuristic removal pattern.
Key insight: to ensure uniqueness, after bulk removal we do GRADUAL removal
with per-step uniqueness check ONLY for the last ~5 removals.
This is 10x faster than checking every single removal.
"""
import json, random, sys, time

rng = random.Random(12345)

def is_valid(b, r, c, v):
    for k in range(9):
        if b[r][k] == v or b[k][c] == v:
            return False
    br, bc = (r//3)*3, (c//3)*3
    for i in range(br, br+3):
        for j in range(bc, bc+3):
            if b[i][j] == v:
                return False
    return True

def count_solutions(board, limit=2):
    count = [0]
    b = [row[:] for row in board]
    def solve():
        if count[0] >= limit:
            return
        for r in range(9):
            for c in range(9):
                if b[r][c] == 0:
                    for v in range(1, 10):
                        if is_valid(b, r, c, v):
                            b[r][c] = v
                            solve()
                            b[r][c] = 0
                            if count[0] >= limit:
                                return
                    return
        count[0] += 1
    solve()
    return count[0]

def complete_board():
    b = [[0]*9 for _ in range(9)]
    def solve():
        for r in range(9):
            for c in range(9):
                if b[r][c] == 0:
                    vals = list(range(1, 10))
                    rng.shuffle(vals)
                    for v in vals:
                        if is_valid(b, r, c, v):
                            b[r][c] = v
                            if solve():
                                return True
                            b[r][c] = 0
                    return False
        return True
    solve()
    return b

def generate_level(base, target_clues):
    """
    Generate a puzzle with target_clues given numbers and guaranteed unique solution.
    Uses a semi-random approach with per-step uniqueness for the critical removals.
    """
    puzzle = [row[:] for row in base]
    cells = [(r, c) for r in range(9) for c in range(9)]
    rng.shuffle(cells)
    
    given = 81
    
    # Phase 1: Fast bulk removal down to ~target + 8
    for r, c in cells:
        if given <= target_clues + 8:
            break
        puzzle[r][c] = 0
        given -= 1
    
    if count_solutions(puzzle, 2) != 1:
        return None  # Already non-unique, abort
    
    # Phase 2: Careful removal with per-step uniqueness check
    for r, c in cells:
        if given <= target_clues:
            break
        if puzzle[r][c] == 0:
            continue
        saved = puzzle[r][c]
        puzzle[r][c] = 0
        if count_solutions(puzzle, 2) == 1:
            given -= 1
        else:
            puzzle[r][c] = saved  # Keep it
    
    # Phase 3: Try to remove more (aggressive) - optional
    # (we accept whatever we got)
    
    return puzzle

TARGETS = [33, 30, 28, 25, 23]
levels = []
start = time.time()

print("Generating 100 unique-solution levels...")
idx = 0
attempts = 0
while idx < 100:
    attempts += 1
    if attempts > 200:
        print("ABORT: too many attempts")
        break
    
    if attempts % 20 == 0:
        elapsed = time.time() - start
        print(f"  [{elapsed:.0f}s] Attempt {attempts}, generated {idx}/100...")
    
    diff = idx // 20
    target = TARGETS[diff]
    
    base = complete_board()
    puzzle = generate_level(base, target)
    
    if puzzle is None:
        continue  # Bulk removal made it non-unique
    
    given = sum(1 for row in puzzle for v in row if v != 0)
    n_sol = count_solutions(puzzle, 2)
    
    if n_sol == 1:
        diff_name = ['初级','中级','高级','专家','大师'][diff]
        print(f"L{idx+1:3d} ({diff_name}) clues={given:2d} ✅")
        levels.append({"p": puzzle, "s": base})
        idx += 1

elapsed = time.time() - start
print(f"\n{'='*40}")
print(f"Generated {len(levels)} levels in {elapsed:.1f}s ({attempts} attempts)")
print(f"✅ All have unique solutions!" if all(count_solutions(l['p'], 2) == 1 for l in levels) else "❌ Some failed!")

with open('/opt/data/projects/sudoku/levels_data.json', 'w') as f:
    json.dump(levels, f)
print("Saved to levels_data.json")
