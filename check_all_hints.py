#!/usr/bin/env python3
import json

with open('levels.json') as f:
    L = json.load(f)

def count_initial_hints(p):
    b = [row[:] for row in p]
    
    def candidates():
        c = [[set() for _ in range(9)] for _ in range(9)]
        for r in range(9):
            for k in range(9):
                if b[r][k]: continue
                s = set(range(1, 10))
                for i in range(9):
                    if b[r][i]: s.discard(b[r][i])
                    if b[i][k]: s.discard(b[i][k])
                br, bk = (r//3)*3, (k//3)*3
                for i in range(3):
                    for j in range(3):
                        if b[br+i][bk+j]: s.discard(b[br+i][bk+j])
                c[r][k] = s
        return c
    
    c = candidates()
    found = []
    
    # Naked Single
    for r in range(9):
        for k in range(9):
            if b[r][k] == 0 and len(c[r][k]) == 1:
                found.append(f"Naked ({r+1},{k+1})")
    
    # Hidden Row
    for r in range(9):
        for v in range(1, 10):
            ks = [k for k in range(9) if b[r][k]==0 and v in c[r][k]]
            if len(ks) == 1:
                found.append(f"Row {r+1} {v}@({r+1},{ks[0]+1})")
    
    # Hidden Col
    for k in range(9):
        for v in range(1, 10):
            rs = [r for r in range(9) if b[r][k]==0 and v in c[r][k]]
            if len(rs) == 1:
                found.append(f"Col {k+1} {v}@({rs[0]+1},{k+1})")
    
    # Hidden Box
    for br in range(0, 9, 3):
        for bk in range(0, 9, 3):
            for v in range(1, 10):
                cells = [(r,k) for r in range(br,br+3) for k in range(bk,bk+3) if b[r][k]==0 and v in c[r][k]]
                if len(cells) == 1:
                    found.append(f"Box {br//3*3+bk//3+1} {v}@({cells[0][0]+1},{cells[0][1]+1})")
    
    return len(found)

def simulate_full_hint(p):
    """Simulate fh() until stuck, return (steps_done, remaining_empty)"""
    b = [row[:] for row in p]
    step = 0
    
    while True:
        c = [[set() for _ in range(9)] for _ in range(9)]
        for r in range(9):
            for k in range(9):
                if b[r][k]: continue
                s = set(range(1, 10))
                for i in range(9):
                    if b[r][i]: s.discard(b[r][i])
                    if b[i][k]: s.discard(b[i][k])
                br, bk = (r//3)*3, (k//3)*3
                for i in range(3):
                    for j in range(3):
                        if b[br+i][bk+j]: s.discard(b[br+i][bk+j])
                c[r][k] = s
        
        found = False
        # Naked Single
        for r in range(9):
            for k in range(9):
                if b[r][k]==0 and len(c[r][k])==1:
                    b[r][k] = list(c[r][k])[0]
                    found = True
                    break
            if found: break
        if found: step += 1; continue
        
        # Hidden Row
        for r in range(9):
            for v in range(1, 10):
                ks = [k for k in range(9) if b[r][k]==0 and v in c[r][k]]
                if len(ks)==1:
                    b[r][ks[0]] = v
                    found = True
                    break
            if found: break
        if found: step += 1; continue
        
        # Hidden Col
        for k in range(9):
            for v in range(1, 10):
                rs = [r for r in range(9) if b[r][k]==0 and v in c[r][k]]
                if len(rs)==1:
                    b[rs[0]][k] = v
                    found = True
                    break
            if found: break
        if found: step += 1; continue
        
        # Hidden Box
        for br in range(0, 9, 3):
            for bk in range(0, 9, 3):
                for v in range(1, 10):
                    cells = [(r,k) for r in range(br,br+3) for k in range(bk,bk+3) if b[r][k]==0 and v in c[r][k]]
                    if len(cells)==1:
                        r, k = cells[0]
                        b[r][k] = v
                        found = True
                        break
                if found: break
            if found: break
        if found: step += 1; continue
        
        remaining = sum(1 for r in range(9) for k in range(9) if b[r][k]==0)
        return step, remaining, b

# Check all levels
print("=== Initial Hint Count & Full Hint Simulation ===")
issues = []
for i, lv in enumerate(L):
    initial = count_initial_hints(lv['p'])
    steps, remaining, _ = simulate_full_hint(lv['p'])
    if remaining > 10 or initial == 0:
        issues.append((i, initial, steps, remaining))
        status = ""
        if initial == 0:
            status = " [NO INITIAL HINTS!]"
        print(f"Level {i+1:3d}: initial={initial:2d}, steps={steps:2d}, remaining={remaining:2d}{status}")

if not issues:
    print("All levels have initial hints and can be fully solved with current strategies! ✓")
else:
    print(f"\n=== {len(issues)} problematic levels ===")
    for i, init, steps, rem in issues:
        print(f"  Level {i+1} (idx {i}): init_hints={init}, steps_before_stuck={steps}, stuck_with={rem} empty")
