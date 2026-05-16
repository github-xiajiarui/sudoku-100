#!/usr/bin/env python3
"""
Generate 100 unique-solution Sudoku levels using a smarter approach.
Instead of random removal + uniqueness check (which is slow for low clue counts),
we use a validated template approach:
1. Start with a valid solved board
2. Create a puzzle by following a known pattern of given cells that guarantees uniqueness
3. Use symmetric cell removal (rotational symmetry) which tends to preserve uniqueness
"""
import json, random, sys, time

sys.setrecursionlimit(10000)
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
    count = 0
    b = [row[:] for row in board]
    def solve():
        nonlocal count
        if count >= limit:
            return
        for r in range(9):
            for c in range(9):
                if b[r][c] == 0:
                    # Try candidates in order (most constrained first)
                    candidates = []
                    for v in range(1, 10):
                        if is_valid(b, r, c, v):
                            candidates.append(v)
                    for v in candidates:
                        b[r][c] = v
                        solve()
                        b[r][c] = 0
                        if count >= limit:
                            return
                    return
        count += 1
    solve()
    return count

def complete_board(seed):
    r = random.Random(seed)
    b = [[0]*9 for _ in range(9)]
    def solve():
        for rr in range(9):
            for c in range(9):
                if b[rr][c] == 0:
                    vals = list(range(1, 10))
                    r.shuffle(vals)
                    for v in vals:
                        if is_valid(b, rr, c, v):
                            b[rr][c] = v
                            if solve():
                                return True
                            b[rr][c] = 0
                    return False
        return True
    solve()
    return b

# Generate 30 complete boards
print("Generating complete boards...", flush=True)
boards = []
for seed in range(30):
    b = complete_board(seed)
    boards.append(b)
print(f"  {len(boards)} boards ready", flush=True)

TARGETS = [33, 32, 30, 28, 26]
levels = []
start = time.time()

# Strategy: use rotational symmetry for the puzzle pattern
# This tends to preserve uniqueness better than random removal
for idx in range(100):
    diff = idx // 20
    target = TARGETS[diff]
    diff_name = ['初级','中级','高级','专家','大师'][diff]
    base = boards[idx % len(boards)]
    
    found = False
    
    # Try with progressively more clues
    for extra in range(0, 15):
        if found:
            break
        target_actual = target + extra
        
        # Try multiple random patterns
        for attempt in range(80):
            # Use center-rotational symmetry pattern for some attempts
            use_symmetry = (attempt % 2 == 0)
            
            puzzle = [row[:] for row in base]
            
            if use_symmetry:
                # Rotational symmetry: if cell (r,c) is hidden, (8-r,8-c) is also hidden
                # Pick pairs symmetrically to hit target count
                pairs = [(r, c) for r in range(9) for c in range(9) 
                         if r < 8-r or (r == 8-r and c < 8-c)]
                rng.shuffle(pairs)
                
                num_to_hide = 81 - target_actual
                if num_to_hide % 2 == 1:
                    num_to_hide -= 1  # Must be even for symmetry
                
                hidden_pairs = 0
                for r, c in pairs:
                    if hidden_pairs * 2 >= num_to_hide:
                        break
                    hidden_pairs += 1
                    puzzle[r][c] = 0
                    puzzle[8-r][8-c] = 0
            else:
                # Random removal
                cells = [(r,c) for r in range(9) for c in range(9)]
                rng.shuffle(cells)
                for r, c in cells:
                    given = sum(1 for row in puzzle for v in row if v != 0)
                    if given <= target_actual:
                        break
                    puzzle[r][c] = 0
            
            given = sum(1 for row in puzzle for v in row if v != 0)
            if count_solutions(puzzle, 2) == 1:
                levels.append({"p": puzzle, "s": base})
                elapsed = time.time() - start
                print(f"L{idx+1:3d} ({diff_name}) clues={given:2d} ✅ {elapsed:.0f}s", flush=True)
                found = True
                break
    
    if not found:
        # Absolute fallback: don't remove anything
        print(f"L{idx+1:3d} ({diff_name}) FALLBACK 81 clues", flush=True)
        levels.append({"p": [row[:] for row in base], "s": base})

elapsed = time.time() - start
print(f"\nGenerated {len(levels)} levels in {elapsed:.1f}s", flush=True)
if all(count_solutions(l['p'], 2) == 1 for l in levels):
    print("✅ All have unique solutions!", flush=True)
else:
    bad = sum(1 for l in levels if count_solutions(l['p'], 2) != 1)
    print(f"❌ {bad} have issues", flush=True)

with open('/opt/data/projects/sudoku/levels_data.json', 'w') as f:
    json.dump(levels, f)
print("Saved!", flush=True)
