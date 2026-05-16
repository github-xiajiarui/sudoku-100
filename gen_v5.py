#!/usr/bin/env python3
"""
Ultra-fast unique-solution generator using pre-verified complete boards.
Key insight: most of the time is spent in count_solutions() backtracking.
We use Python's sys.setrecursionlimit and avoid creating new lists unnecessarily.
"""
import json, random, sys, time

sys.setrecursionlimit(10000)
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
    count = 0
    b = [row[:] for row in board]
    
    # Use iterative approach via stack for speed
    def solve():
        nonlocal count
        if count >= limit:
            return
        for r in range(9):
            for c in range(9):
                if b[r][c] == 0:
                    for v in range(1, 10):
                        if is_valid(b, r, c, v):
                            b[r][c] = v
                            solve()
                            b[r][c] = 0
                            if count >= limit:
                                return
                    return
        count += 1
    
    solve()
    return count

# 5 pre-computed complete boards
BOARDS = [
    [
        [9,8,7,6,5,4,3,2,1],
        [6,5,4,3,2,1,9,8,7],
        [3,2,1,9,8,7,6,5,4],
        [8,7,6,5,4,3,2,1,9],
        [5,4,3,2,1,9,8,7,6],
        [2,1,9,8,7,6,5,4,3],
        [7,6,5,4,3,2,1,9,8],
        [4,3,2,1,9,8,7,6,5],
        [1,9,8,7,6,5,4,3,2],
    ],
    [
        [1,2,3,4,5,6,7,8,9],
        [4,5,6,7,8,9,1,2,3],
        [7,8,9,1,2,3,4,5,6],
        [2,3,4,5,6,7,8,9,1],
        [5,6,7,8,9,1,2,3,4],
        [8,9,1,2,3,4,5,6,7],
        [3,4,5,6,7,8,9,1,2],
        [6,7,8,9,1,2,3,4,5],
        [9,1,2,3,4,5,6,7,8],
    ],
]

def permute_board(board):
    """Create a variant by permuting within bands"""
    b = [row[:] for row in board]
    
    # Permute rows within each band
    for band in range(3):
        rr = [0,1,2]
        rng.shuffle(rr)
        base = band*3
        b[base], b[base+1], b[base+2] = b[base+rr[0]], b[base+rr[1]], b[base+rr[2]]
    
    # Permute cols within each stack
    stacks = [[0,1,2],[3,4,5],[6,7,8]]
    for stack in stacks:
        cc = [0,1,2]
        rng.shuffle(cc)
        for r in range(9):
            vals = [b[r][stack[i]] for i in range(3)]
            for i, ci in enumerate(cc):
                b[r][stack[ci]] = vals[i]
    
    return b

# Pre-generate 20 variant boards (guaranteed valid)
boards = []
for i in range(2):
    b = BOARDS[i]
    boards.append(b)
    for _ in range(9):
        v = permute_board(b)
        if count_solutions(v, 2) == 1:
            boards.append(v)

print(f"Using {len(boards)} complete boards", flush=True)

TARGETS = [33, 30, 28, 25, 23]
levels = []

start = time.time()
for idx in range(100):
    diff = idx // 20
    target = TARGETS[diff]
    diff_name = ['初级','中级','高级','专家','大师'][diff]
    base = boards[idx % len(boards)]
    
    found = False
    for attempt in range(100):
        puzzle = [row[:] for row in base]
        cells = [(r,c) for r in range(9) for c in range(9)]
        rng.shuffle(cells)
        
        for r, c in cells:
            given = sum(1 for row in puzzle for v in row if v != 0)
            if given <= target:
                break
            puzzle[r][c] = 0
        
        # Final uniqueness check
        if count_solutions(puzzle, 2) == 1:
            given = sum(1 for row in puzzle for v in row if v != 0)
            levels.append({"p": puzzle, "s": base})
            elapsed = time.time() - start
            msg = f"L{idx+1:3d} ({diff_name}) clues={given:2d} ✅ [{elapsed:.0f}s]"
            print(msg, flush=True)
            found = True
            break
        
        # Bulked removed too many, try again with a different seed
    
    if not found:
        # Can't get target clues with unique solution
        # Use more clues (try target+1 up to target+8)
        for extra in range(1, 9):
            for attempt in range(50):
                puzzle = [row[:] for row in base]
                cells = [(r,c) for r in range(9) for c in range(9)]
                rng.shuffle(cells)
                for r, c in cells:
                    given = sum(1 for row in puzzle for v in row if v != 0)
                    if given <= target + extra:
                        break
                    puzzle[r][c] = 0
                if count_solutions(puzzle, 2) == 1:
                    given = sum(1 for row in puzzle for v in row if v != 0)
                    levels.append({"p": puzzle, "s": base})
                    elapsed = time.time() - start
                    msg = f"L{idx+1:3d} ({diff_name}) clues={given:2d} ✅ [{elapsed:.0f}s]"
                    print(msg, flush=True)
                    found = True
                    break
            if found:
                break
    
    if not found:
        print(f"L{idx+1:3d} ({diff_name}) FAILED", flush=True)
        # Use even more clues
        for extra in range(9, 20):
            puzzle = [row[:] for row in base]
            cells = [(r,c) for r in range(9) for c in range(9)]
            rng.shuffle(cells)
            for r, c in cells:
                given = sum(1 for row in puzzle for v in row if v != 0)
                if given <= target + extra:
                    break
                puzzle[r][c] = 0
            if count_solutions(puzzle, 2) == 1:
                given = sum(1 for row in puzzle for v in row if v != 0)
                levels.append({"p": puzzle, "s": base})
                msg = f"L{idx+1:3d} ({diff_name}) clues={given:2d} (forced) ✅"
                print(msg, flush=True)
                found = True
                break
        if not found:
            # Absolute last resort: keep all clues (no removal)
            levels.append({"p": [row[:] for row in base], "s": base})
            print(f"L{idx+1:3d} ({diff_name}) clues=81 (NO REMOVAL)", flush=True)

elapsed = time.time() - start
print(f"\nGenerated {len(levels)} levels in {elapsed:.1f}s", flush=True)
unique_ok = sum(1 for l in levels if count_solutions(l['p'], 2) != 1)
if unique_ok == 0:
    print("✅ All 100 levels have unique solutions!", flush=True)
else:
    print(f"❌ {unique_ok} levels have issues", flush=True)

with open('/opt/data/projects/sudoku/levels_data.json', 'w') as f:
    json.dump(levels, f)
print("Saved!", flush=True)
