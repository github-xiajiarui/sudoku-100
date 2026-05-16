#!/usr/bin/env python3
"""预生成100关数独数据并嵌入HTML"""
import json, random

random.seed(42)

def shuffle(a):
    for i in range(len(a)-1,0,-1):
        j = random.randint(0,i)
        a[i],a[j] = a[j],a[i]

def valid(b,r,c,n):
    for i in range(9):
        if b[r][i]==n or b[i][c]==n: return False
    br,bc = (r//3)*3,(c//3)*3
    for i in range(br,br+3):
        for j in range(bc,bc+3):
            if b[i][j]==n: return False
    return True

def solve(b):
    for r in range(9):
        for c in range(9):
            if b[r][c]==0:
                nums=list(range(1,10))
                shuffle(nums)
                for n in nums:
                    if valid(b,r,c,n):
                        b[r][c]=n
                        if solve(b): return True
                        b[r][c]=0
                return False
    return True

def count_solutions(b,limit=2):
    cnt=[0]
    def dfs():
        for r in range(9):
            for c in range(9):
                if b[r][c]==0:
                    for n in range(1,10):
                        if valid(b,r,c,n):
                            b[r][c]=n
                            dfs()
                            b[r][c]=0
                            if cnt[0]>=limit: return
                    return
        cnt[0]+=1
    dfs()
    return cnt[0]

def generate_level(clues):
    sol = [[0]*9 for _ in range(9)]
    solve(sol)
    puz = [row[:] for row in sol]
    cells = [(r,c) for r in range(9) for c in range(9)]
    shuffle(cells)
    removed = 0
    target = 81 - clues
    for r,c in cells:
        if removed >= target: break
        backup = puz[r][c]
        puz[r][c]=0
        test = [row[:] for row in puz]
        if count_solutions(test,2)==1:
            removed+=1
        else:
            puz[r][c]=backup
    return puz, sol

DIFFICULTIES = [
    ("初级", 28, 20),
    ("中级", 26, 20),
    ("高级", 24, 20),
    ("专家", 22, 20),
    ("大师", 20, 20),
]

all_levels = []
total = 0
for name, clues, count in DIFFICULTIES:
    for i in range(count):
        puz, sol = generate_level(clues)
        all_levels.append({"p":puz,"s":sol})
        total += 1
        print(f"  {name} {i+1}/{count} 生成完成 ({total}/100)")

output = json.dumps(all_levels, separators=(',',':'))
print(f"\n共生成{total}关，数据大小: {len(output)} 字节")
print(output[:100])
