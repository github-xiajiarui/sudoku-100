#!/usr/bin/env python3
"""
Fast unique-solution Sudoku level generator.
Strategy: start with complete boards, use a fast random removal + unique check.
Each removal checks uniqueness via backtracking limited to 2 solutions.
"""
import json, random, sys, time

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

def complete_board(rng):
    """Generate a random complete valid board using backtracking"""
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

# Pre-generate complete boards
rng = random.Random(42)
print("Generating complete boards...")
complete_boards = []
while len(complete_boards) < 100:
    b = complete_board(rng)
    if count_solutions(b, 2) == 1:
        complete_boards.append(b)
    if len(complete_boards) % 10 == 0:
        print(f"  {len(complete_boards)}/100")

# Difficulty targets
TARGETS = [33, 30, 27, 25, 22]  # 初级->大师
levels = []
errors = 0

for idx in range(100):
    base = complete_boards[idx]
    difficulty_idx = idx // 20
    target = TARGETS[difficulty_idx]
    diff_name = ['初级','中级','高级','专家','大师'][difficulty_idx]
    
    puzzle = [row[:] for row in base]
    cells = [(r, c) for r in range(9) for c in range(9)]
    rng.shuffle(cells)
    
    removed = 0
    target_removed = 81 - target
    
    for r, c in cells:
        if sum(1 for row in puzzle for v in row if v != 0) <= target:
            break
        saved = puzzle[r][c]
        puzzle[r][c] = 0
        if count_solutions(puzzle, 2) != 1:
            puzzle[r][c] = saved
    
    given = sum(1 for row in puzzle for v in row if v != 0)
    
    # Verify final
    n_sol = count_solutions(puzzle, 2)
    ok = n_sol == 1
    if not ok:
        errors += 1
    
    levels.append({"p": puzzle, "s": base})
    print(f"L{idx+1:3d} ({diff_name}) clues={given:2d} sol={n_sol} {'✅' if ok else '❌'}")

with open('/opt/data/projects/sudoku/levels_data.json', 'w') as f:
    json.dump(levels, f)

print(f"\n{'='*40}")
print(f"Total: {len(levels)} levels, {errors} errors" if errors == 0 else f"Total: {len(levels)} levels, {errors} ERRORS!")
print(f"{'✅ All unique!' if errors == 0 else '❌ Some have issues'}")
