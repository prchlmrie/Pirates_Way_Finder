"""
Manual Grid Editor
Allows you to manually mark cells as walkable (0) or wall (1)
"""

import json
import sys

def load_grid(grid_path="app/static/grid.json"):
    """Load the grid from JSON"""
    with open(grid_path, "r") as f:
        return json.load(f)

def save_grid(grid_data, grid_path="app/static/grid.json"):
    """Save the grid to JSON"""
    with open(grid_path, "w") as f:
        json.dump(grid_data, f)
    print(f"Grid saved to {grid_path}")

def mark_area(grid_data, x_start, y_start, x_end, y_end, value):
    """
    Mark a rectangular area as walkable (0) or wall (1)
    
    Args:
        x_start, y_start: Top-left corner (in grid cells)
        x_end, y_end: Bottom-right corner (in grid cells)
        value: 0 for walkable, 1 for wall
    """
    grid = grid_data["grid"]
    
    # Ensure coordinates are within bounds
    x_start = max(0, min(x_start, grid_data["width"] - 1))
    y_start = max(0, min(y_start, grid_data["height"] - 1))
    x_end = max(0, min(x_end, grid_data["width"] - 1))
    y_end = max(0, min(y_end, grid_data["height"] - 1))
    
    count = 0
    for y in range(y_start, y_end + 1):
        for x in range(x_start, x_end + 1):
            grid[y][x] = value
            count += 1
    
    label = "walkable" if value == 0 else "wall"
    print(f"Marked {count} cells as {label} in area ({x_start},{y_start}) to ({x_end},{y_end})")
    
    return grid_data

def pixel_to_grid(px, py, cell_size=20):
    """Convert pixel coordinates to grid cell coordinates"""
    return px // cell_size, py // cell_size

def show_grid_info(grid_data):
    """Show current grid statistics"""
    grid = grid_data["grid"]
    walkable = sum(row.count(0) for row in grid)
    walls = sum(row.count(1) for row in grid)
    total = walkable + walls
    
    print(f"\n=== Grid Info ===")
    print(f"Dimensions: {grid_data['width']}x{grid_data['height']} cells")
    print(f"Cell size: {grid_data['cell_size']}x{grid_data['cell_size']} pixels")
    print(f"Walkable: {walkable} cells ({walkable/total*100:.1f}%)")
    print(f"Walls: {walls} cells ({walls/total*100:.1f}%)")

# Interactive mode
if __name__ == "__main__":
    print("=== Manual Grid Editor ===\n")
    print("Loading grid data...")
    
    # Load the grid into a variable that will be available in interactive mode
    grid_data = load_grid()
    show_grid_info(grid_data)
    
    print("\n=== Ready for Editing! ===")
    print("The grid is loaded in variable: grid_data")
    print("")
    print("Available commands:")
    print("  mark_area(grid_data, x_start, y_start, x_end, y_end, value)")
    print("  save_grid(grid_data)")
    print("  show_grid_info(grid_data)")
    print("  pixel_to_grid(px, py, cell_size=20)")
    print("")
    print("Example:")
    print("  >>> grid_data = mark_area(grid_data, 51, 30, 52, 34, 0)")
    print("  >>> save_grid(grid_data)")
    print("")
    print("Type your commands below, or 'exit()' to quit\n")

