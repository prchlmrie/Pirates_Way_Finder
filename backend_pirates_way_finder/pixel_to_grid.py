"""
Pixel to Grid Coordinate Converter
Helps you convert pixel coordinates to grid cells for editing
"""

import json

def load_grid_info():
    with open("app/static/grid.json", "r") as f:
        data = json.load(f)
    return data["cell_size"]

def convert_coords():
    cell_size = load_grid_info()
    
    print(f"=== Pixel to Grid Converter (Cell size: {cell_size}px) ===\n")
    
    # Get pixel coordinates
    print("Enter pixel coordinates from your map:")
    px1 = int(input("  Start X (pixels): "))
    py1 = int(input("  Start Y (pixels): "))
    px2 = int(input("  End X (pixels): "))
    py2 = int(input("  End Y (pixels): "))
    
    # Convert to grid
    gx1 = px1 // cell_size
    gy1 = py1 // cell_size
    gx2 = px2 // cell_size
    gy2 = py2 // cell_size
    
    print(f"\n=== Grid Coordinates ===")
    print(f"Start: ({gx1}, {gy1})")
    print(f"End: ({gx2}, {gy2})")
    
    # Generate command
    print(f"\n=== Copy this command ===")
    print(f"grid_data = mark_area(grid_data, {gx1}, {gy1}, {gx2}, {gy2}, value=?)")
    print("\nReplace '?' with:")
    print("  0 = Walkable (green)")
    print("  1 = Wall (red)")
    
    print(f"\nArea size: {abs(gx2-gx1)+1}×{abs(gy2-gy1)+1} cells")
    print(f"           {abs(px2-px1)}×{abs(py2-py1)} pixels")

if __name__ == "__main__":
    convert_coords()

