import json

# Load grid
with open('app/static/grid.json', 'r') as f:
    g = json.load(f)

print(f"Grid: {g['width']}x{g['height']} cells")
print(f"Cell size: {g['cell_size']}px")

walkable = sum(row.count(0) for row in g['grid'])
walls = sum(row.count(1) for row in g['grid'])
total = walkable + walls

print(f"Walkable: {walkable:,} ({walkable/total*100:.1f}%)")
print(f"Walls: {walls:,} ({walls/total*100:.1f}%)")



