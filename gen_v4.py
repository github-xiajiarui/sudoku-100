#!/usr/bin/env python3
"""
Efficient unique-solution generator using 15 pre-verified complete boards
with careful gradual removal.
The key optimization: pre-generate 15 good boards, then for each target clue count,
start with target+10 clues and do per-step removal.
"""
import json, random, sys, time

rng = random.Random(42)

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

# Generate 10 complete boards
print("Generating complete boards...")
boards = []
for seed in range(10):
    b = complete_board(seed)
    boards.append(b)
print(f"  {len(boards)} boards ready")

TARGETS = [33, 30, 28, 25, 23]
levels = []

start = time.time()

for idx in range(100):
    diff = idx // 20
    target = TARGETS[diff]
    diff_name = ['初级','中级','高级','专家','大师'][diff]
    
    base = boards[idx % len(boards)]
    
    # Try to generate puzzle for this target
    found = False
    for attempt in range(50):
        puzzle = [row[:] for row in base]
        cells = [(r, c) for r in range(9) for c in range(9)]
        rng.shuffle(cells)
        
        # Start with a few clues removed, then gradually remove more
        # Only remove when uniqueness is verified
        for r, c in cells:
            given = sum(1 for row in puzzle for v in row if v != 0)
            if given <= target:
                break
            saved = puzzle[r][c]
            puzzle[r][c] = 0
            if count_solutions(puzzle, 2) != 1:
                puzzle[r][c] = saved
        
        given = sum(1 for row in puzzle for v in row if v != 0)
        n_sol = count_solutions(puzzle, 2)
        
        if n_sol == 1:
            levels.append({"p": puzzle, "s": base})
            elapsed = time.time() - start
            print(f"L{idx+1:3d} ({diff_name}) clues={given:2d} ✅ [{elapsed:.0f}s]")
            found = True
            break
    
    if not found:
        # Can't hit target, try with more clues
        for attempt in range(50):
            puzzle = [row[:] for row in base]
            cells = [(r, c) for r in range(9) for c in range(9)]
            rng.shuffle(cells)
            
            for r, c in cells:
                given = sum(1 for row in puzzle for v in row if v != 0)
                if given <= target + 3:
                    break
                saved = puzzle[r][c]
                puzzle[r][c] = 0
                if count_solutions(puzzle, 2) != 1:
                    puzzle[r][c] = saved
            
            given = sum(1 for row in puzzle for v in row if v != 0)
            n_sol = count_solutions(puzzle, 2)
            if n_sol == 1:
                levels.append({"p": puzzle, "s": base})
                elapsed = time.time() - start
                print(f"L{idx+1:3d} ({diff_name}) clues={given:2d} (+{given-target}) ✅ [{elapsed:.0f}s]")
                found = True
                break
        
        if not found:
            # Last resort: give up on target, accept whatever gives unique
            print(f"L{idx+1:3d} ({diff_name}) FAILED after 100 attempts")
            # Use one more clue
            for attempt in range(20):
                puzzle = [row[:] for row in base]
                cells = [(r, c) for r in range(9) for c in range(9)]
                rng.shuffle(cells)
                for r, c in cells:
                    given = sum(1 for row in puzzle for v in row if v != 0)
                    if given <= target + 5:
                        break
                    saved = puzzle[r][c]
                    puzzle[r][c] = 0
                    if count_solutions(puzzle, 2) != 1:
                        puzzle[r][c] = saved
                given = sum(1 for row in puzzle for v in row if v != 0)
                if count_solutions(puzzle, 2) == 1:
                    levels.append({"p": puzzle, "s": base})
                    print(f"L{idx+1:3d} ({diff_name}) clues={given:2d} (forced) ✅")
                    found = True
                    break

elapsed = time.time() - start
print(f"\n{'='*40}")
print(f"Generated {len(levels)} levels in {elapsed:.1f}s")
unique_ok = all(count_solutions(l['p'], 2) == 1 for l in levels)
print(f"{'✅ All unique!' if unique_ok else '❌ Some have issues'}")

with open('/opt/data/projects/sudoku/levels_data.json', 'w') as f:
    json.dump(levels, f)
