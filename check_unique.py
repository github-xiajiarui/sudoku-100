import json

with open('/opt/data/projects/sudoku/levels_data.json') as f:
    data = json.load(f)

def count_solutions(puzzle, limit=2):
    """Count solutions using backtracking, stop at limit"""
    board = [row[:] for row in puzzle]
    count = 0
    
    def solve():
        nonlocal count
        if count >= limit:
            return
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    for v in range(1, 10):
                        ok = True
                        for k in range(9):
                            if board[r][k] == v or board[k][c] == v:
                                ok = False
                                break
                        if ok:
                            br, bc = (r//3)*3, (c//3)*3
                            for i in range(br, br+3):
                                for j in range(bc, bc+3):
                                    if board[i][j] == v:
                                        ok = False
                                        break
                                if not ok:
                                    break
                        if ok:
                            board[r][c] = v
                            solve()
                            board[r][c] = 0
                            if count >= limit:
                                return
                    return
        count += 1
    
    solve()
    return count

multi_solutions = []
for idx, level in enumerate(data):
    p = level['p']
    n = count_solutions(p, 2)
    if n != 1:
        multi_solutions.append((idx+1, n))
        print(f"Level {idx+1}: {n} solutions")

if not multi_solutions:
    print("✅ All 100 levels have unique solutions!")
else:
    print(f"\n❌ {len(multi_solutions)} levels with non-unique solutions:")
    for l, n in multi_solutions:
        print(f"  Level {l}: {n} solutions")
