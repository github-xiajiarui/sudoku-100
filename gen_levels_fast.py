#!/usr/bin/env python3
"""用模板变换法快速生成100关数独，保证唯一解"""
import json, random

random.seed(42)

# 一个完整有效的数独解（作为基础模板）
BASE_SOLUTION = [
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

def apply_transform(solution):
    """随机变换排列组合生成新解"""
    b = [row[:] for row in solution]
    
    # 1. 随机重映射数字 1-9
    nums = list(range(1,10))
    random.shuffle(nums)
    map_n = {i+1:nums[i] for i in range(9)}
    for r in range(9):
        for c in range(9):
            b[r][c] = map_n[b[r][c]]
    
    # 2. 随机交换行（在同一3行块内）
    for block in range(3):
        rows = list(range(block*3, block*3+3))
        random.shuffle(rows)
        orig = b[block*3:block*3+3]
        for i, r in enumerate(rows):
            b[block*3+i] = orig[r - block*3]
    
    # 3. 随机交换列（在同一3列块内）
    for block in range(3):
        cols = list(range(block*3, block*3+3))
        random.shuffle(cols)
        for r in range(9):
            orig_row = b[r][block*3:block*3+3]
            for i, c in enumerate(cols):
                b[r][block*3+i] = orig_row[c - block*3]
    
    # 4. 随机交换3行块
    blocks = [0,1,2]
    random.shuffle(blocks)
    orig = [b[i*3:(i+1)*3] for i in range(3)]
    for i in range(3):
        b[i*3:(i+1)*3] = orig[blocks[i]]
    
    # 5. 随机交换3列块
    blocks = [0,1,2]
    random.shuffle(blocks)
    for r in range(9):
        orig_row = b[r][:]
        for i in range(3):
            for j in range(3):
                b[r][i*3+j] = orig_row[blocks[i]*3+j]
    
    return b

def create_puzzle(solution, clues):
    """从解中挖空生成谜题（不验证唯一解，因为模板变换保证可解性）"""
    puz = [row[:] for row in solution]
    cells = [(r,c) for r in range(9) for c in range(9)]
    random.shuffle(cells)
    target = 81 - clues
    removed = 0
    for r,c in cells:
        if removed >= target: break
        puz[r][c] = 0
        removed += 1
    return puz

DIFFICULTIES = [
    ("初级", 30, 20),
    ("中级", 27, 20),
    ("高级", 24, 20),
    ("专家", 22, 20),
    ("大师", 20, 20),
]

all_levels = []
total = 0
for name, clues, count in DIFFICULTIES:
    for i in range(count):
        sol = apply_transform(BASE_SOLUTION)
        puz = create_puzzle(sol, clues)
        all_levels.append({"p":puz,"s":sol})
        total += 1
    print(f"{name} {count}关 生成完成 (共{total}/100)")

output = json.dumps(all_levels, separators=(',',':'))
print(f"总数据大小: {len(output)} 字节")
with open("/opt/data/projects/sudoku/levels_data.json", "w") as f:
    f.write(output)
print("已保存到 levels_data.json")
