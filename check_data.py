import json

with open('/opt/data/projects/sudoku/levels_data.json') as f:
    data = json.load(f)

print(f"Total levels: {len(data)}")
print()

errors = 0
for idx, level in enumerate(data):
    p = level['p']
    s = level['s']
    
    # Check 1: s is a valid solution (1-9 in each row, col, box)
    def check_valid(board):
        for r in range(9):
            row_set = set()
            for c in range(9):
                v = board[r][c]
                if v < 1 or v > 9:
                    return False, f"value {v} out of range at ({r},{c})"
                if v in row_set:
                    return False, f"duplicate {v} in row {r}"
                row_set.add(v)
        for c in range(9):
            col_set = set()
            for r in range(9):
                v = board[r][c]
                if v in col_set:
                    return False, f"duplicate {v} in col {c}"
                col_set.add(v)
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                box_set = set()
                for r in range(br, br+3):
                    for c in range(bc, bc+3):
                        v = board[r][c]
                        if v in box_set:
                            return False, f"duplicate {v} in box {br//3}-{bc//3}"
                        box_set.add(v)
        return True, "ok"
    
    valid, reason = check_valid(s)
    if not valid:
        errors += 1
        print(f"Level {idx+1}: INVALID solution - {reason}")
        continue
    
    # Check 2: p matches s (puzzle should be subset of solution)
    for r in range(9):
        for c in range(9):
            if p[r][c] != 0 and p[r][c] != s[r][c]:
                errors += 1
                print(f"Level {idx+1}: p[{r}][{c}]={p[r][c]} != s[{r}][{c}]={s[r][c]}")
                break
        else:
            continue
        break

if errors == 0:
    print("✅ All 100 levels have valid solutions!")
else:
    print(f"\n❌ {errors} levels with errors")
