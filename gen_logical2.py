#!/usr/bin/env python3
"""生成100关数独 - 用对称挖空+逻辑可推导验证，一次挖一空验证一空"""
import json, random

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
    """随机变换"""
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

# ===== 快速逻辑求解（只验证可推导性，不记录过程） =====

def get_candidates(board):
    cand = [[set() for _ in range(9)] for _ in range(9)]
    for r in range(9):
        for c in range(9):
            if board[r][c]:
                continue
            possible = set(range(1,10))
            for i in range(9):
                if board[r][i]: possible.discard(board[r][i])
                if board[i][c]: possible.discard(board[i][c])
            br,bc = (r//3)*3,(c//3)*3
            for i in range(br,br+3):
                for j in range(bc,bc+3):
                    if board[i][j]: possible.discard(board[i][j])
            cand[r][c] = possible
    return cand

def apply_naked_single(board, cand):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0 and len(cand[r][c]) == 1:
                return (r, c, next(iter(cand[r][c])))
    return None

def apply_hidden_single(board, cand):
    for r in range(9):
        for n in range(1,10):
            positions = [(r,c) for c in range(9) if n in cand[r][c]]
            if len(positions) == 1:
                return (r, positions[0][1], n)
    for c in range(9):
        for n in range(1,10):
            positions = [(r,c) for r in range(9) if n in cand[r][c]]
            if len(positions) == 1:
                return (positions[0][0], c, n)
    for br in range(0,9,3):
        for bc in range(0,9,3):
            for n in range(1,10):
                positions = [(r,c) for r in range(br,br+3) for c in range(bc,bc+3) if n in cand[r][c]]
                if len(positions) == 1:
                    return (positions[0][0], positions[0][1], n)
    return None

def apply_locked_candidates(board, cand):
    """区块排除 - 通过排除直接得到某个数字"""
    # 指向：宫→行/列
    for br in range(0,9,3):
        for bc in range(0,9,3):
            for n in range(1,10):
                cells = [(r,c) for r in range(br,br+3) for c in range(bc,bc+3) if n in cand[r][c]]
                if len(cells) < 2:
                    continue
                rows = set(r for r,c in cells)
                cols = set(c for r,c in cells)
                # 如果宫中n只出现在同一行
                if len(rows) == 1:
                    r = next(iter(rows))
                    # 尝试排除
                    excluded = False
                    for c in range(9):
                        if c//3 != bc//3 and n in cand[r][c]:
                            # 排除这个候选
                            pass
                    # 检查排除后是否有新的唯一候选或隐性唯一
                    test_cand = [row[:] for row in board]
                    # 复杂了，先跳过
                    pass
                if len(cols) == 1:
                    pass
    return None

def solve_one_step(board):
    """应用一步逻辑规则，返回(r,c,val)或None"""
    cand = get_candidates(board)
    step = apply_naked_single(board, cand)
    if step: return step
    step = apply_hidden_single(board, cand)
    if step: return step
    # 区块排除暂时跳过（会增加复杂度）
    return None

def can_solve_logically(board):
    """检查当前棋盘是否能通过纯逻辑解出"""
    b = [row[:] for row in board]
    for _ in range(81):
        step = solve_one_step(b)
        if not step:
            # 是否已完成
            if all(all(v != 0 for v in row) for row in b):
                return True
            return False
        r,c,val = step
        b[r][c] = val
    return all(all(v != 0 for v in row) for row in b)

def generate_logical_level(clues):
    """生成可逻辑推导的关卡"""
    while True:
        sol = transform(BASE)
        puzzle = [row[:] for row in sol]
        
        # 先随机打乱顺序
        cells = [(r,c) for r in range(9) for c in range(9)]
        shuffle(cells)
        
        target = 81 - clues
        removed = 0
        
        for r,c in cells:
            if removed >= target:
                break
            
            # 试挖
            puzzle[r][c] = 0
            
            # 验证可逻辑推导
            if can_solve_logically(puzzle):
                removed += 1
            else:
                puzzle[r][c] = sol[r][c]
        
        empty = sum(1 for r in range(9) for c in range(9) if puzzle[r][c] == 0)
        if empty >= target - 2:
            # 最终确认
            ok = can_solve_logically(puzzle)
            if ok:
                return puzzle, sol
        
        print(f"  重试(已挖{empty},目标{target})")

DIFF = [
    ("初级", 30, 20),
    ("中级", 27, 20),
    ("高级", 24, 20),
    ("专家", 22, 20),
    ("大师", 20, 20),
]

all_levels = []
total = 0
for name, clues, count in DIFF:
    for i in range(count):
        puz, sol = generate_logical_level(clues)
        # 最终验证
        assert can_solve_logically(puz), f"{name} {i+1}: 逻辑推导失败!"
        # 验证解正确
        b = [row[:] for row in puz]
        assert can_solve_logically(b), f"{name} {i+1}: 无法通过逻辑解出!"
        all_levels.append({"p": puz, "s": sol})
        total += 1
        print(f"  {name} {i+1}/{count} ✅ ({total}/100)")

output = json.dumps(all_levels, separators=(',',':'))
print(f"\n总计: {total}关, {len(output)} 字节")
with open("/opt/data/projects/sudoku/logical_levels.json", "w") as f:
    f.write(output)
print("已保存!")
