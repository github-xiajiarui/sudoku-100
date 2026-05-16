#!/usr/bin/env python3
"""
Generate 100 Sudoku levels with UNIQUE solutions.
Strategy:
1. Start with a known valid complete board
2. Remove numbers one by one, verifying unique solution after each removal
3. Stop when we've removed enough clues for the target difficulty
"""
import json, random, copy

def is_valid(board, r, c, v):
    for k in range(9):
        if board[r][k] == v or board[k][c] == v:
            return False
    br, bc = (r//3)*3, (c//3)*3
    for i in range(br, br+3):
        for j in range(bc, bc+3):
            if board[i][j] == v:
                return False
    return True

FULL_BOARDS = [
    # 10 pre-verified complete boards
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
]

def count_solutions(board, limit=2):
    """Count solutions up to limit"""
    count = 0
    
    def solve(b):
        nonlocal count
        if count >= limit:
            return
        for r in range(9):
            for c in range(9):
                if b[r][c] == 0:
                    for v in range(1, 10):
                        if is_valid(b, r, c, v):
                            b[r][c] = v
                            solve(b)
                            b[r][c] = 0
                            if count >= limit:
                                return
                    return
        count += 1
    
    b = [row[:] for row in board]
    solve(b)
    return count

def shuffle_board(base):
    """Create a valid complete board by permuting rows/cols within bands"""
    b = [row[:] for row in base]
    # Permute rows within each band (3-row groups)
    for band in range(3):
        rows = [band*3, band*3+1, band*3+2]
        random.shuffle(rows)
        b[band*3], b[band*3+1], b[band*3+2] = b[rows[0]], b[rows[1]], b[rows[2]]
    # Permute columns within each stack
    for stack in range(3):
        cols = [stack*3, stack*3+1, stack*3+2]
        random.shuffle(cols)
        for r in range(9):
            vals = [b[r][stack*3], b[r][stack*3+1], b[r][stack*3+2]]
            b[r][stack*3] = vals[cols.index(stack*3)]
            b[r][stack*3+1] = vals[cols.index(stack*3+1)]
            b[r][stack*3+2] = vals[cols.index(stack*3+2)]
    return b

random.seed(42)
levels = []

# Difficulty: number of given clues
# 初级 33-36, 中级 30-32, 高级 27-29, 专家 24-26, 大师 22-23
TARGETS = [33, 30, 27, 25, 22]

for difficulty_idx, target_clues in enumerate(TARGETS):
    for level_in_difficulty in range(20):
        idx = difficulty_idx * 20 + level_in_difficulty
        
        while True:
            # Start with a valid complete board
            if idx < 2:
                base = FULL_BOARDS[idx]
            else:
                base = shuffle_board(random.choice(FULL_BOARDS))
            
            # Verify it's valid
            if count_solutions(base, 2) != 1:
                continue
            
            # Generate a unique-solution puzzle by removing clues
            puzzle = [row[:] for row in base]
            cells = [(r, c) for r in range(9) for c in range(9)]
            random.shuffle(cells)
            
            for r, c in cells:
                if sum(1 for row in puzzle for v in row if v != 0) <= target_clues:
                    break
                saved = puzzle[r][c]
                puzzle[r][c] = 0
                if count_solutions(puzzle, 2) != 1:
                    puzzle[r][c] = saved  # can't remove, put back
            
            given = sum(1 for row in puzzle for v in row if v != 0)
            
            # Accept within range
            if target_clues - 3 <= given <= target_clues + 2:
                break
            # If too few clues given, retry with different base
        
        levels.append({"p": puzzle, "s": base})
        
        given = sum(1 for row in puzzle for v in row if v != 0)
        diff_name = ['初级','中级','高级','专家','大师'][difficulty_idx]
        print(f"Level {idx+1} ({diff_name}): {given} given clues — {'OK' if count_solutions(puzzle, 2) == 1 else 'UNIQUE CHECK FAILED'}")

with open('/opt/data/projects/sudoku/levels_data.json', 'w') as f:
    json.dump(levels, f)

print(f"\n✅ Generated {len(levels)} levels with unique solutions!")
