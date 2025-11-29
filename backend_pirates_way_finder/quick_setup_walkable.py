"""
Quick setup script to mark basic walkable areas
Including the starting point at (504, 2302)
"""

import json
from pathlib import Path

# Load grid
print("Loading grid...")
with open('app/static/grid.json', 'r') as f:
    grid_data = json.load(f)

print(f"Grid: {grid_data['width']}x{grid_data['height']} cells")
print(f"Cell size: {grid_data['cell_size']}px")

# Convert pixel to grid coordinates
cell_size = grid_data['cell_size']

def pixel_to_grid(px, py):
    return px // cell_size, py // cell_size

def mark_area(x_start, y_start, x_end, y_end, value):
    """Mark rectangular area as walkable (0) or wall (1)"""
    grid = grid_data["grid"]
    count = 0
    
    # Ensure coordinates are within bounds
    x_start = max(0, min(x_start, grid_data["width"] - 1))
    y_start = max(0, min(y_start, grid_data["height"] - 1))
    x_end = max(0, min(x_end, grid_data["width"] - 1))
    y_end = max(0, min(y_end, grid_data["height"] - 1))
    
    for y in range(y_start, y_end + 1):
        for x in range(x_start, x_end + 1):
            grid[y][x] = value
            count += 1
    
    label = "walkable" if value == 0 else "wall"
    print(f"   Marked {count} cells as {label} in area ({x_start},{y_start}) to ({x_end},{y_end})")

print("\nMarking walkable areas starting from (504, 2302)...")
print("=" * 60)

# Starting point area (504, 2302) - YOUR specified starting point
start_gx, start_gy = pixel_to_grid(504, 2302)
print(f"\n1. ⭐ Starting point area at (504, 2302):")
print(f"   Pixel: (504, 2302) → Grid: ({start_gx}, {start_gy})")
mark_area(start_gx - 10, start_gy - 10, start_gx + 10, start_gy + 10, 0)

# Mark vertical corridor going up from starting point
print(f"\n2. Main vertical corridor (going north):")
mark_area(start_gx - 5, start_gy - 50, start_gx + 5, start_gy + 5, 0)

# Mark vertical corridor going down from starting point
print(f"\n3. Main vertical corridor (going south):")
mark_area(start_gx - 5, start_gy - 5, start_gx + 5, start_gy + 20, 0)

# Mark horizontal corridors
print(f"\n4. Main horizontal corridor (going west):")
mark_area(start_gx - 50, start_gy - 5, start_gx + 5, start_gy + 5, 0)

print(f"\n5. Main horizontal corridor (going east):")
mark_area(start_gx - 5, start_gy - 5, start_gx + 50, start_gy + 5, 0)

# Mark some test destination areas spread across the map
print(f"\n6. Test destination areas across the map:")
mark_area(20, 20, 30, 30, 0)      # Top left
mark_area(100, 50, 110, 60, 0)    # Top center
mark_area(20, 200, 30, 210, 0)    # Bottom left
mark_area(100, 200, 110, 210, 0)  # Bottom center

# Connect them with corridors
print(f"\n7. Connecting corridors:")
mark_area(20, 20, 22, 210, 0)     # Left vertical spine
mark_area(100, 50, 102, 210, 0)   # Center vertical spine
mark_area(20, 50, 110, 52, 0)     # Top horizontal
mark_area(20, 200, 110, 202, 0)   # Bottom horizontal

print("\n" + "=" * 60)
print("Statistics:")
print("=" * 60)

walkable = sum(row.count(0) for row in grid_data['grid'])
walls = sum(row.count(1) for row in grid_data['grid'])
total = walkable + walls

print(f"Walkable: {walkable:,} ({walkable/total*100:.1f}%)")
print(f"Walls: {walls:,} ({walls/total*100:.1f}%)")

# Save
print(f"\nSaving grid...")
with open('app/static/grid.json', 'w') as f:
    json.dump(grid_data, f)

print(f"✅ Grid saved!")
print("\n" + "=" * 60)
print("NEXT STEPS:")
print("=" * 60)
print("\n1. Visualize the grid:")
print("   python visualize_grid.py")
print("   Open: grid_visualization.png")
print()
print("2. Add more walkable areas if needed:")
print("   python edit_grid.py")
print()
print("3. Restart backend:")
print("   python main.py")
print()
print("4. Test pathfinding:")
print("   python test_path_endpoint.py")
print()
print("=" * 60)

