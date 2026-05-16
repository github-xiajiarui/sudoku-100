#!/usr/bin/env python3
"""生成100关 - 挖空适中 + 逻辑可推导验证"""
import json, random, sys

random.seed(42)

BASE = [
    [1,2,3,4,5,6,7,8,9],
    [4,5,6,7,8,9,1,2,3],
    [7,8,9,1,2,3,4,5,6],
    [2,3,1,5,6,4,8,9,7],
    [5,6,4,8,9,7,2,3,1],
    [8,9,7,2,3,1,5,6,4],
    [3,1,2,6,4,5,9,7,8],
    [6,4,5,9,7,8,3,1,2],
    [9,7,8,3,1,2,6,4,5],
]

def shuffle(a):
    for i in range(len(a)-1,0,-1):
        j = random.randint(0,i)
        a[i],a[j] = a[j],a[i]

def transform(b):
    b = [row[:] for row in b]
    nums = list(range(1,10)); shuffle(nums)
    mp = {i+1:nums[i] for i in range(9)}
    for r in range(9):
        for c in range(9):
            b[r][c] = mp[b[r][c]]
    for blk in range(3):
        rows = list(range(blk*3, blk*3+3)); shuffle(rows)
        orig = [b[i] for i in range(blk*3, blk*3+3)]
        for i,r in enumerate(rows):
            b[blk*3+i] = orig[r-blk*3]
    for blk in range(3):
        cols = list(range(blk*3, blk*3+3)); shuffle(cols)
        for r in range(9):
            orig = [b[r][c] for c in range(blk*3, blk*3+3)]
            for i,c in enumerate(cols):
                b[r][blk*3+i] = orig[c-blk*3]
    blks = [0,1,2]; shuffle(blks)
    orig = [b[i*3:(i+1)*3] for i in range(3)]
    for i in range(3):
        b[i*3:(i+1)*3] = orig[blks[i]]
    blks = [0,1,2]; shuffle(blks)
    for r in range(9):
        orig = b[r][:]
        for i in range(3):
            for j in range(3):
                b[r][i*3+j] = orig[blks[i]*3+j]
    return b

# ===== 逻辑求解 =====
def compute_candidates(board):
    cand = [[set() for _ in range(9)] for _ in range(9)]
    for r in range(9):
        for c in range(9):
            if board[r][c]: continue
            s = set(range(1,10))
            for i in range(9):
                if board[r][i]: s.discard(board[r][i])
                if board[i][c]: s.discard(board[i][c])
            br,bc = (r//3)*3,(c//3)*3
            for i in range(br,br+3):
                for j in range(bc,bc+3):
                    if board[i][j]: s.discard(board[i][j])
            cand[r][c] = s
    return cand

def solve_one_step(board):
    cand = compute_candidates(board)
    # Naked Single
    for r in range(9):
        for c in range(9):
            if board[r][c]==0 and len(cand[r][c])==1:
                return (r,c,next(iter(cand[r][c])),'single')
    # Hidden Single - 行
    for r in range(9):
        for n in range(1,10):
            cols = [c for c in range(9) if n in cand[r][c]]
            if len(cols)==1: return (r,cols[0],n,'hidden_row')
    # Hidden Single - 列
    for c in range(9):
        for n in range(1,10):
            rows = [r for r in range(9) if n in cand[r][c]]
            if len(rows)==1: return (rows[0],c,n,'hidden_col')
    # Hidden Single - 宫
    for br in range(0,9,3):
        for bc in range(0,9,3):
            for n in range(1,10):
                cells = [(r,c) for r in range(br,br+3) for c in range(bc,bc+3) if n in cand[r][c]]
                if len(cells)==1: return (cells[0][0],cells[0][1],n,'hidden_box')
    return None

def can_solve(board):
    b = [row[:] for row in board]
    for _ in range(81):
        step = solve_one_step(b)
        if not step:
            return all(all(v!=0 for v in row) for row in b)
        r,c,v,_ = step
        b[r][c] = v
    return True

# 难度配置：适当提高初始数字数量，保证可推导
DIFF = [
    ("初级", 33, 20),   # 48空
    ("中级", 30, 20),   # 51空
    ("高级", 28, 20),   # 53空
    ("专家", 26, 20),   # 55空
    ("大师", 24, 20),   # 57空
]

all_levels = []
total = 0
for name, clues, count in DIFF:
    for i in range(count):
        while True:
            sol = transform(BASE)
            puzzle = [row[:] for row in sol]
            cells = [(r,c) for r in range(9) for c in range(9)]
            shuffle(cells)
            target = 81 - clues
            removed = 0
            for r,c in cells:
                if removed >= target: break
                puzzle[r][c] = 0
                if can_solve(puzzle):
                    removed += 1
                else:
                    puzzle[r][c] = sol[r][c]
            empty = sum(1 for r in range(9) for c in range(9) if puzzle[r][c]==0)
            if empty >= target - 1:
                ok = can_solve(puzzle)
                if ok:
                    all_levels.append({"p": puzzle, "s": sol})
                    total += 1
                    print(f"  {name} {i+1}/{count} ✅ {empty}空({total}/100)")
                    break
            sys.stdout.flush()

output = json.dumps(all_levels, separators=(',',':'))
print(f"\n总计: {total}关, {len(output)} 字节")
with open("/opt/data/projects/sudoku/logical_levels.json", "w") as f:
    f.write(output)
print("已保存!")
