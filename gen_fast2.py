#!/usr/bin/env python3
"""
Fastest unique-solution generator.
Strategy: pre-generate complete boards quickly, then for each one:
1. Remove clues in bulk for speed
2. Check uniqueness once at the end
3. If not unique, discard and regenerate
This is faster because we don't check uniqueness after every single removal.
"""
import json, random, sys, time

rng = random.Random(99)

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

def make_puzzle_fast(base, target_clues):
    """Remove clues in random order, bulk removal, then verify unique at end."""
    cells = [(r, c) for r in range(9) for c in range(9)]
    rng.shuffle(cells)
    puzzle = [row[:] for row in base]
    
    removed = 0
    target_removed = 81 - target_clues
    
    # --- Phase 1: Bulk removal (remove many at once) ---
    # Remove down to target_clues + buffer
    buffer = 5
    bulk_target = target_clues + buffer
    for r, c in cells:
        given = sum(1 for row in puzzle for v in row if v != 0)
        if given <= bulk_target:
            break
        puzzle[r][c] = 0
    
    # --- Phase 2: Slow removal with uniqueness check ---
    # We actually don't check per-removal; we try to reach target_clues
    # then check at the end
    for r, c in cells:
        if puzzle[r][c] == 0:
            continue
        given = sum(1 for row in puzzle for v in row if v != 0)
        if given <= target_clues:
            break
        puzzle[r][c] = 0
    
    return puzzle

TARGETS = [33, 30, 27, 25, 22]
levels = []
attempts = 0

print("Generating 100 unique-solution levels...")
start = time.time()

idx = 0
while idx < 100:
    attempts += 1
    if attempts > 500:
        print("TOO MANY ATTEMPTS, aborting")
        break
    
    if attempts % 50 == 0:
        print(f"  Attempt {attempts}, generated {idx}/100...")
    
    base = complete_board()
    diff = idx // 20
    target = TARGETS[min(diff, 4)]
    
    puzzle = make_puzzle_fast(base, target)
    given = sum(1 for row in puzzle for v in row if v != 0)
    
    n_sol = count_solutions(puzzle, 2)
    if n_sol == 1:
        diff_name = ['初级','中级','高级','专家','大师'][diff]
        print(f"L{idx+1:3d} ({diff_name}) clues={given:2d} ✅ (attempt {attempts})")
        levels.append({"p": puzzle, "s": base})
        idx += 1
    else:
        # Retry with same base but fewer removed cells
        for buffer in range(1, 8):
            puzzle2 = make_puzzle_fast(base, target + buffer)
            given2 = sum(1 for row in puzzle2 for v in row if v != 0)
            n_sol2 = count_solutions(puzzle2, 2)
            if n_sol2 == 1:
                diff_name = ['初级','中级','高级','专家','大师'][diff]
                print(f"L{idx+1:3d} ({diff_name}) clues={given2:2d} ✅ (retry buffer={buffer})")
                levels.append({"p": puzzle2, "s": base})
                idx += 1
                break

elapsed = time.time() - start
print(f"\n✅ Generated {len(levels)} levels in {elapsed:.1f}s ({attempts} total attempts)")

with open('/opt/data/projects/sudoku/levels_data.json', 'w') as f:
    json.dump(levels, f)
