#!/usr/bin/env python3
"""Verify that the enhanced hint system (with backtracking fallback) can solve all levels."""
import json, copy, sys

with open('levels.json') as f:
    L = json.load(f)

def solve_grid(grid):
    """Backtracking solver, returns True if exactly 1 solution exists."""
    g = [row[:] for row in grid]
    sol_count = [0]
    
    def is_valid(r, c, v):
        for i in range(9):
            if g[r][i] == v or g[i][c] == v:
                return False
        br, bc = (r//3)*3, (c//3)*3
        for i in range(3):
            for j in range(3):
                if g[br+i][bc+j] == v:
                    return False
        return True
    
    def bt():
        if sol_count[0] > 1:
            return
        for r in range(9):
            for c in range(9):
                if g[r][c] == 0:
                    for v in range(1, 10):
                        if is_valid(r, c, v):
                            g[r][c] = v
                            bt()
                            g[r][c] = 0
                            if sol_count[0] > 1:
                                return
                    return
        sol_count[0] += 1
    
    bt()
    return sol_count[0] == 1

def candidates(grid):
    c = [[set() for _ in range(9)] for _ in range(9)]
    for r in range(9):
        for k in range(9):
            if grid[r][k]: continue
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

def find_hint(grid):
    """Simulates the enhanced fh() including backtracking fallback."""
    b = [row[:] for row in grid]
    c = candidates(b)
    
    # 1. Naked Single
    for r in range(9):
        for k in range(9):
            if b[r][k] == 0 and len(c[r][k]) == 1:
                return r, k, list(c[r][k])[0], 'naked'
    
    # 2. Hidden Row
    for r in range(9):
        for v in range(1, 10):
            ks = [k for k in range(9) if b[r][k]==0 and v in c[r][k]]
            if len(ks) == 1:
                return r, ks[0], v, 'hidden_row'
    
    # 3. Hidden Col
    for k in range(9):
        for v in range(1, 10):
            rs = [r for r in range(9) if b[r][k]==0 and v in c[r][k]]
            if len(rs) == 1:
                return rs[0], k, v, 'hidden_col'
    
    # 4. Hidden Box
    for br in range(0, 9, 3):
        for bk in range(0, 9, 3):
            for v in range(1, 10):
                cells = [(r,k) for r in range(br,br+3) for k in range(bk,bk+3) if b[r][k]==0 and v in c[r][k]]
                if len(cells) == 1:
                    return cells[0][0], cells[0][1], v, 'hidden_box'
    
    # 5. Backtracking fallback
    best_r, best_c, best_size = -1, -1, 10
    for r in range(9):
        for k in range(9):
            if b[r][k] == 0 and 0 < len(c[r][k]) < best_size:
                best_r, best_c, best_size = r, k, len(c[r][k])
    
    if best_r >= 0:
        for tv in sorted(c[best_r][best_c]):
            test_grid = [row[:] for row in b]
            test_grid[best_r][best_c] = tv
            if solve_grid(test_grid):
                return best_r, best_c, tv, 'trial'
    
    return None, None, None, None

def simulate_level(p):
    """Apply find_hint repeatedly until solved or stuck."""
    b = [row[:] for row in p]
    steps = 0
    used_trial = False
    
    while True:
        remaining = sum(1 for r in range(9) for k in range(9) if b[r][k] == 0)
        if remaining == 0:
            return True, steps, used_trial
        
        r, c, v, kind = find_hint(b)
        if r is None:
            return False, steps, used_trial
        
        b[r][c] = v
        steps += 1
        if kind == 'trial':
            used_trial = True

# Check all levels
print("Checking all 100 levels with enhanced hint system...")
bad = []
trial_needed = []
for i, lv in enumerate(L):
    ok, steps, used_trial = simulate_level(lv['p'])
    if not ok:
        bad.append(i)
        print(f"  Level {i+1}: FAILED after {steps} steps (still stuck)")
    else:
        if used_trial:
            trial_needed.append(i+1)

if bad:
    print(f"\nFAILED: {len(bad)} levels still cannot be solved!")
    for idx in bad:
        print(f"  Level {idx+1}")
else:
    print(f"\nAll 100 levels can be solved! ✓")
    if trial_needed:
        print(f"  {len(trial_needed)} levels need backtracking fallback:")
        print(f"  {trial_needed}")
    else:
        print("  No levels need backtracking fallback.")
