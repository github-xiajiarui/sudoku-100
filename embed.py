#!/usr/bin/env python3
import json, os

# Load 100 levels data
with open('/opt/data/projects/sudoku/levels_data.json') as f:
    levels = json.load(f)

# Read template
with open('/opt/data/projects/sudoku/template_hint.html') as f:
    html = f.read()

# Replace placeholder with data
data_str = json.dumps(levels, separators=(',',':'))
html = html.replace("__LEVELS_DATA__", data_str)

with open('/opt/data/projects/sudoku/index.html', 'w') as f:
    f.write(html)

print(f"Written: {os.path.getsize('/opt/data/projects/sudoku/index.html')} bytes")
print(f"Levels: {len(levels)}")
