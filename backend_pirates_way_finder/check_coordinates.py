"""
Check if node coordinates are in walkable cells
"""
import json
from app.core.database import nodes_collection

# Load grid
with open("app/static/grid.json", "r") as f:
    grid_data = json.load(f)

grid = grid_data["grid"]
cell_size = grid_data["cell_size"]

print(f"=== Checking Node Coordinates ===")
print(f"Grid: {grid_data['width']}x{grid_data['height']} cells")
print(f"Cell size: {cell_size}px\n")

nodes = list(nodes_collection.find({"_meta.is_archived": {"$ne": True}}))

for node in nodes:
    props = node.get("properties", {})
    coords = node.get("geometry", {}).get("coordinates", [])
    
    if coords:
        name = props.get("name", "Unknown")
        x, y = coords[0], coords[1]
        
        # Convert to grid coordinates
        grid_x = x // cell_size
        grid_y = y // cell_size
        
        # Check if in bounds
        if 0 <= grid_x < grid_data['width'] and 0 <= grid_y < grid_data['height']:
            cell_value = grid[grid_y][grid_x]
            status = "WALKABLE" if cell_value == 0 else "BLOCKED (WALL)"
            symbol = "[OK]" if cell_value == 0 else "[BLOCKED]"
            
            print(f"{symbol} {name}")
            print(f"   Pixel: [{x}, {y}]")
            print(f"   Grid: [{grid_x}, {grid_y}]")
            print(f"   Status: {status}")
            print()
        else:
            print(f"[OUT OF BOUNDS] {name}")
            print(f"   Pixel: [{x}, {y}]")
            print(f"   Grid: [{grid_x}, {grid_y}]")
            print(f"   Status: OUT OF BOUNDS!")
            print()

