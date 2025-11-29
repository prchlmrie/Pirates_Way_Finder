"""
Find stair-related nodes in MongoDB and suggest areas to mark
"""
from app.core.database import nodes_collection
import json

print("=" * 60)
print("STAIR DETECTION TOOL")
print("=" * 60)

# Load grid
with open("app/static/grid.json", "r") as f:
    grid_data = json.load(f)

cell_size = grid_data["cell_size"]
print(f"\nGrid: {grid_data['width']}x{grid_data['height']} cells ({cell_size}px each)")
print()

# Search for stairs, steps, ramps
keywords = ["stair", "step", "ramp", "elevator", "escalator"]
print("Searching MongoDB for accessibility-related nodes...")
print("-" * 60)

found_nodes = []

for keyword in keywords:
    nodes = list(nodes_collection.find({
        "$or": [
            {"properties.name": {"$regex": keyword, "$options": "i"}},
            {"properties.id": {"$regex": keyword, "$options": "i"}},
            {"properties.tags": {"$regex": keyword, "$options": "i"}}
        ],
        "_meta.is_archived": {"$ne": True}
    }))
    
    if nodes:
        print(f"\nFound {len(nodes)} node(s) with '{keyword}':")
        for node in nodes:
            props = node.get("properties", {})
            coords = node.get("geometry", {}).get("coordinates", [])
            
            if coords:
                name = props.get("name", "Unknown")
                x, y = coords[0], coords[1]
                gx, gy = x // cell_size, y // cell_size
                
                # Check if it's a ramp or stairs
                node_type = "[RAMP]" if "ramp" in name.lower() else "[STAIRS]"
                
                print(f"  {node_type}: {name}")
                print(f"     Pixel: [{x}, {y}]")
                print(f"     Grid: [{gx}, {gy}]")
                
                found_nodes.append({
                    "name": name,
                    "type": "ramp" if "ramp" in name.lower() else "stairs",
                    "pixel": [x, y],
                    "grid": [gx, gy]
                })

print()
print("=" * 60)
print("RECOMMENDATIONS")
print("=" * 60)

# Separate ramps and stairs
ramps = [n for n in found_nodes if n["type"] == "ramp"]
stairs = [n for n in found_nodes if n["type"] == "stairs"]

if ramps:
    print(f"\n[OK] Found {len(ramps)} RAMP node(s) - these are accessible!")
    for ramp in ramps:
        print(f"   {ramp['name']} at grid {ramp['grid']}")

if stairs:
    print(f"\n[WARN] Found {len(stairs)} STAIR node(s) - mark these to avoid in accessibility mode!")
    print("\nAdd these to STAIR_AREAS in app/services/pathfinding.py:")
    print()
    
    for stair in stairs:
        gx, gy = stair["grid"]
        # Add a buffer around the stair node (±5 cells)
        x1, y1 = max(0, gx - 5), max(0, gy - 5)
        x2, y2 = min(grid_data['width'], gx + 5), min(grid_data['height'], gy + 5)
        
        print(f"    ({x1}, {y1}, {x2}, {y2}),  # {stair['name']}")
else:
    print("\n[WARN] No stair nodes found in MongoDB!")
    print("   You may need to manually identify stair locations on your map.")
    print("   Use: python mark_stairs.py")

if not found_nodes:
    print("\n[INFO] NO accessibility-related nodes found in MongoDB")
    print("   This means your map may not have stair/ramp nodes defined.")
    print()
    print("   OPTION 1: Add stair nodes to MongoDB")
    print("   OPTION 2: Manually mark stair areas on the map image")
    print()
    print("   To manually mark stairs:")
    print("   1. Open app/static/map.png")
    print("   2. Find staircase locations (look for stair symbols)")
    print("   3. Run: python mark_stairs.py")
    print("   4. Follow prompts to add coordinates")

print()
print("=" * 60)

