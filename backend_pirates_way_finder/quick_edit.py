"""
Quick Grid Editor - Edit specific areas quickly
"""

import json

def edit_grid():
    # Load grid
    with open("app/static/grid.json", "r") as f:
        grid_data = json.load(f)
    
    print("=== Quick Grid Editor ===\n")
    print(f"Grid: {grid_data['width']}x{grid_data['height']} cells")
    print(f"Cell size: {grid_data['cell_size']}px")
    
    # Get user input
    print("\nEnter coordinates (in grid cells):")
    x_start = int(input("  X start: "))
    y_start = int(input("  Y start: "))
    x_end = int(input("  X end: "))
    y_end = int(input("  Y end: "))
    
    print("\nWhat should this area be?")
    print("  0 = Walkable (green)")
    print("  1 = Wall (red)")
    value = int(input("  Enter 0 or 1: "))
    
    # Apply changes
    grid = grid_data["grid"]
    count = 0
    for y in range(y_start, y_end + 1):
        for x in range(x_start, x_end + 1):
            if 0 <= x < grid_data['width'] and 0 <= y < grid_data['height']:
                grid[y][x] = value
                count += 1
    
    print(f"\nChanged {count} cells to {'walkable' if value == 0 else 'wall'}")
    
    # Save
    with open("app/static/grid.json", "w") as f:
        json.dump(grid_data, f)
    
    print("Grid saved!")
    
    # Ask to visualize
    viz = input("\nVisualize the grid? (y/n): ")
    if viz.lower() == 'y':
        import subprocess
        subprocess.run(["python", "visualize_grid.py"])

if __name__ == "__main__":
    edit_grid()

