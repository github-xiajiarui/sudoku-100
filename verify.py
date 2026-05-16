import json, sys
sys.setrecursionlimit(10000)

def is_valid(b, r, c, v):
    for k in range(9):
        if b[r][k] == v or b[k][c] == v: return False
    br, bc = (r//3)*3, (c//3)*3
    for i in range(br, br+3):
        for j in range(bc, bc+3):
            if b[i][j] == v: return False
    return True

def count_solutions(board, limit=2):
    count = 0
    b = [row[:] for row in board]
    def solve():
        nonlocal count
        if count >= limit: return
        for r in range(9):
            for c in range(9):
                if b[r][c] == 0:
                    for v in range(1, 10):
                        if is_valid(b, r, c, v):
                            b[r][c] = v
                            solve()
                            b[r][c] = 0
                            if count >= limit: return
                    return
        count += 1
    solve()
    return count

with open('/opt/data/projects/sudoku/levels_data.json') as f:
    data = json.load(f)

print(f"Levels: {len(data)}")
bad = []
for i, l in enumerate(data):
    given = sum(1 for r in l['p'] for v in r if v != 0)
    n = count_solutions(l['p'], 2)
    if n != 1:
        bad.append((i+1, given, n))
        print(f"L{i+1}: {given} clues, {n} solutions ❌")
    else:
        print(f"L{i+1}: {given} clues ✅")

if not bad:
    print(f"\n✅ All {len(data)} levels have unique solutions!")
else:
    print(f"\n❌ {len(bad)} levels have issues: {bad}")
