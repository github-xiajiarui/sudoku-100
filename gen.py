#!/usr/bin/env python3
"""Generate 100 sudoku puzzles with unique solutions, increasing difficulty."""
import json, random, time, sys
random.seed(42)  # reproducible

N=9

def is_valid(b,r,c,n):
    for i in range(N):
        if b[r][i]==n or b[i][c]==n: return False
    br,bc=r//3*3,c//3*3
    for i in range(3):
        for j in range(3):
            if b[br+i][bc+j]==n: return False
    return True

def solve_fast(b):
    """Solve with MRV heuristic."""
    best_r=best_c=-1
    min_options=10
    for r in range(N):
        for c in range(N):
            if b[r][c]!=0: continue
            opts=0
            for n in range(1,10):
                if is_valid(b,r,c,n): opts+=1
            if opts==0: return False
            if opts<min_options:
                min_options=opts; best_r=r; best_c=c
                if opts==1: break
        if min_options==1: break
    if best_r==-1: return True
    r,c=best_r,best_c
    for n in range(1,10):
        if is_valid(b,r,c,n):
            b[r][c]=n
            if solve_fast(b): return True
    b[r][c]=0
    return False

def solve_first(b):
    """Find first solution (no shuffle)."""
    for r in range(N):
        for c in range(N):
            if b[r][c]!=0: continue
            for n in range(1,10):
                if is_valid(b,r,c,n):
                    b[r][c]=n
                    if solve_first(b): return True
            b[r][c]=0
            return False
    return True

def count_upto2(b):
    """Count solutions, stop at 2."""
    count=0
    def dfs(br,cr):
        nonlocal count
        if count>=2: return
        # find empty cell
        r=c=-1
        for r2 in range(N):
            found=False
            for c2 in range(N):
                if br[r2][c2]==0:
                    r,c=r2,c2; found=True; break
            if found: break
        if r==-1: count+=1; return
        for n in range(1,10):
            if is_valid(br,r,c,n):
                br[r][c]=n
                dfs(br,cr)
                br[r][c]=0
                if count>=2: return
    dfs([row[:] for row in b],0)
    return count

full_cache=[]

def make_full():
    board=[[0]*N for _ in range(N)]
    solve_fast(board)
    return board

def generate_puzzle(clues):
    full=make_full()
    cells=[(r,c) for r in range(N) for c in range(N)]
    random.shuffle(cells)
    puzzle=[row[:] for row in full]
    removed=0
    for r,c in cells:
        backup=puzzle[r][c]
        puzzle[r][c]=0
        if count_upto2(puzzle)==1:
            removed+=1
            if removed>=81-clues: break
        else:
            puzzle[r][c]=backup
    return puzzle, full

configs=[
    (1,20,28,32,"初级"),
    (21,40,26,28,"中级"),
    (41,60,24,26,"高级"),
    (61,80,22,24,"专家"),
    (81,100,20,22,"大师")
]

def main():
    levels=[]
    t0=time.time()
    for s,e,minC,maxC,diff in configs:
        print(f"\nGenerating {diff} (levels {s}-{e}, clues {minC}-{maxC})...", file=sys.stderr)
        while len(levels)<e:
            clues=random.randint(minC,maxC)
            ts=time.time()
            puzzle,solution=generate_puzzle(clues)
            dt=time.time()-ts
            levels.append({"p":puzzle,"s":solution,"d":diff,"i":len(levels)+1})
            print(f"  #{len(levels)} ({clues} clues) in {dt:.1f}s", file=sys.stderr)
    print(f"\nTotal: {len(levels)} levels in {time.time()-t0:.1f}s", file=sys.stderr)
    with open("/opt/data/projects/sudoku/levels.json","w") as f:
        json.dump(levels, f, separators=(',',':'))
    print("Saved!", file=sys.stderr)
    print("DONE", flush=True)

if __name__=="__main__":
    main()
