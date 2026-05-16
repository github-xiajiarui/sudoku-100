#!/usr/bin/env python3
"""生成100关数独，保证每关每步都可以通过逻辑推导求解"""
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
    """随机变换生成新解"""
    b = [row[:] for row in b]
    nums = list(range(1,10)); shuffle(nums)
    mp = {i+1:nums[i] for i in range(9)}
    for r in range(9):
        for c in range(9):
            b[r][c] = mp[b[r][c]]
    for blk in range(3):
        rows = list(range(blk*3, blk*3+3)); shuffle(rows)
        orig = b[blk*3:blk*3+3]
        for i,r in enumerate(rows):
            b[blk*3+i] = orig[r-blk*3]
    for blk in range(3):
        cols = list(range(blk*3, blk*3+3)); shuffle(cols)
        for r in range(9):
            orig = b[r][blk*3:blk*3+3]
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

# ===== 逻辑求解器 =====

def get_candidates(board):
    """计算每个空格的候选数"""
    cand = [[set() for _ in range(9)] for _ in range(9)]
    for r in range(9):
        for c in range(9):
            if board[r][c]:
                continue
            possible = set(range(1,10))
            # 行排除
            for i in range(9):
                if board[r][i]:
                    possible.discard(board[r][i])
            # 列排除
            for i in range(9):
                if board[i][c]:
                    possible.discard(board[i][c])
            # 宫排除
            br,bc = (r//3)*3,(c//3)*3
            for i in range(br,br+3):
                for j in range(bc,bc+3):
                    if board[i][j]:
                        possible.discard(board[i][j])
            cand[r][c] = possible
    return cand

def apply_naked_single(board, cand):
    """唯一候选数：某个空格只剩下1个候选数"""
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0 and len(cand[r][c]) == 1:
                val = next(iter(cand[r][c]))
                return (r, c, val, f"R{r+1}C{c+1} 只有 {val} 可以填（唯一候选数）")
    return None

def apply_hidden_single(board, cand):
    """隐式唯一：在行/列/宫中，某个数字只出现在一个候选位置"""
    # 行
    for r in range(9):
        for n in range(1,10):
            positions = [(r,c) for c in range(9) if n in cand[r][c]]
            if len(positions) == 1:
                c = positions[0][1]
                return (r, c, n, f"第{r+1}行中 {n} 只能放在 R{r+1}C{c+1}（隐性唯一）")
    # 列
    for c in range(9):
        for n in range(1,10):
            positions = [(r,c) for r in range(9) if n in cand[r][c]]
            if len(positions) == 1:
                r = positions[0][0]
                return (r, c, n, f"第{c+1}列中 {n} 只能放在 R{r+1}C{c+1}（隐性唯一）")
    # 宫
    for br in range(0,9,3):
        for bc in range(0,9,3):
            for n in range(1,10):
                positions = [(r,c) for r in range(br,br+3) for c in range(bc,bc+3) if n in cand[r][c]]
                if len(positions) == 1:
                    r,c = positions[0]
                    return (r, c, n, f"第{br//3+1}宫中 {n} 只能放在 R{r+1}C{c+1}（隐性唯一）")
    return None

def apply_locked_candidates(board, cand):
    """区块排除：
    指向(Pointing): 宫中某数字只出现在同一行/列→排除该行/列其他位置
    宣称(Claiming): 行/列中某数字只出现在同一宫→排除该宫其他位置
    """
    # 指向：宫→行
    for br in range(0,9,3):
        for bc in range(0,9,3):
            for n in range(1,10):
                cells = [(r,c) for r in range(br,br+3) for c in range(bc,bc+3) if n in cand[r][c]]
                if len(cells) == 0:
                    continue
                rows = set(r for r,c in cells)
                cols = set(c for r,c in cells)
                # 如果都在同一行，可以检查该行其他位置
                if len(rows) == 1:
                    r = next(iter(rows))
                    # 这个数字在宫中只出现在第r行，那么该行其他列可以排除n
                    # 但这不是直接填数，而是候选数排除。我们需要找到"通过排除后能直接填数"的情况
                    # 这里只返回排除信息，供get_deduction使用
                    pass
                if len(cols) == 1:
                    pass
    return None

def solve_with_logic(board):
    """用逻辑规则求解，返回每一步的推导信息
    返回: (是否完全解出, 推导步骤列表, 最终棋盘)
    """
    b = [row[:] for row in board]
    steps = []
    
    while True:
        cand = get_candidates(b)
        
        # 检查是否完成
        if all(all(v != 0 for v in row) for row in b):
            return True, steps, b
        
        # 应用规则
        step = apply_naked_single(b, cand)
        if not step:
            step = apply_hidden_single(b, cand)
        # 暂时不用locked candidates等高级规则（足够日常难度）
        
        if not step:
            # 无法继续逻辑推导
            return False, steps, b
        
        r,c,val,reason = step
        b[r][c] = val
        steps.append((r,c,val,reason))
    
    return True, steps, b

def generate_logical_level(clues):
    """生成一关，保证每一步都可以逻辑推导"""
    while True:
        sol = transform(BASE)
        puzzle = [row[:] for row in sol]
        cells = [(r,c) for r in range(9) for c in range(9)]
        shuffle(cells)
        target = 81 - clues
        removed = 0
        
        for r,c in cells:
            if removed >= target:
                break
            
            # 试挖
            puzzle[r][c] = 0
            
            # 检查是否仍可逻辑推导
            solvable, steps, final = solve_with_logic(puzzle)
            
            if solvable and final == sol:
                # 可逻辑推导且解正确
                removed += 1
            else:
                # 不行，恢复
                puzzle[r][c] = sol[r][c]
        
        # 检查是否挖到了目标数量
        empty_count = sum(1 for r in range(9) for c in range(9) if puzzle[r][c] == 0)
        if empty_count >= target - 2:  # 允许少量偏差
            return puzzle, sol
        
        print(f"  重试, 已挖{empty_count}, 目标{target}")

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
        # 验证
        ok, steps, final = solve_with_logic(puz)
        assert ok and final == sol, f"{name} {i+1}: 逻辑推导失败!"
        all_levels.append({"p": puz, "s": sol})
        total += 1
    print(f"{name} {count}关 完成 ({total}/100)")

output = json.dumps(all_levels, separators=(',',':'))
print(f"总数据: {len(output)} 字节")
with open("/opt/data/projects/sudoku/logical_levels.json", "w") as f:
    f.write(output)
print("已保存!")
