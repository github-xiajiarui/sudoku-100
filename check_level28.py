#!/usr/bin/env python3
import json

with open('levels.json') as f:
    L = json.load(f)

p = L[27]['p']
grid = [row[:] for row in p]

def candidates(grid):
    c = [[set() for _ in range(9)] for _ in range(9)]
    for r in range(9):
        for k in range(9):
            if grid[r][k]:
                continue
            s = set(range(1, 10))
            for i in range(9):
                if grid[r][i]: s.discard(grid[r][i])
                if grid[i][k]: s.discard(grid[i][k])
            br, bk = (r//3)*3, (k//3)*3
            for i in range(3):
                for j in range(3):
                    if grid[br+i][bk+j]: s.discard(grid[br+i][bk+j])
            c[r][k] = s
    return c

c = candidates(grid)

# Check Naked Singles
print("=== Naked Singles (唯一候选数) ===")
found = False
for r in range(9):
    for k in range(9):
        if grid[r][k] == 0 and len(c[r][k]) == 1:
            print(f"  ({r+1},{k+1}): {list(c[r][k])}")
            found = True
if not found:
    print("  None found")

# Check Hidden Singles in rows
print("\n=== Hidden Singles - Rows ===")
found = False
for r in range(9):
    for v in range(1, 10):
        cols = [k for k in range(9) if grid[r][k] == 0 and v in c[r][k]]
        if len(cols) == 1:
            print(f"  Row {r+1}: {v} only at ({r+1},{cols[0]+1})")
            found = True
if not found:
    print("  None found")

# Check Hidden Singles in columns
print("\n=== Hidden Singles - Cols ===")
found = False
for k in range(9):
    for v in range(1, 10):
        rows = [r for r in range(9) if grid[r][k] == 0 and v in c[r][k]]
        if len(rows) == 1:
            print(f"  Col {k+1}: {v} only at ({rows[0]+1},{k+1})")
            found = True
if not found:
    print("  None found")

# Check Hidden Singles in boxes
print("\n=== Hidden Singles - Boxes ===")
found = False
for br in range(0, 9, 3):
    for bk in range(0, 9, 3):
        for v in range(1, 10):
            cells = []
            for r in range(br, br+3):
                for k in range(bk, bk+3):
                    if grid[r][k] == 0 and v in c[r][k]:
                        cells.append((r, k))
            if len(cells) == 1:
                print(f"  Box {br//3*3+bk//3+1}: {v} only at ({cells[0][0]+1},{cells[0][1]+1})")
                found = True
if not found:
    print("  None found")

print("\n=== All candidates for empty cells ===")
for r in range(9):
    for k in range(9):
        if grid[r][k] == 0:
            print(f"  ({r+1},{k+1}): {sorted(c[r][k])}")
