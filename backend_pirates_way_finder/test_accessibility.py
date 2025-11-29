"""
Quick test script to verify accessibility features are working correctly.
Run this to check if stairs and ramps are being detected from MongoDB.
"""

from app.core.database import nodes_collection
from app.services.pathfinding_astar import get_ramp_locations, get_stair_blocked_cells
from app.core.grid_loader import grid_instance

# Load grid first
try:
    grid_instance.load("app/static/grid.json")
    print(f"✅ Grid loaded: {grid_instance.w}x{grid_instance.h} cells")
except Exception as e:
    print(f"❌ Error loading grid: {e}")
    exit(1)

print("\n" + "="*60)
print("ACCESSIBILITY FEATURE TEST")
print("="*60)

# Test ramp detection
print("\n🔍 Testing RAMP detection...")
ramp_locations = get_ramp_locations()
if ramp_locations:
    print(f"✅ Found {len(ramp_locations)} ramp location(s):")
    for rx, ry in ramp_locations:
        print(f"   - Grid [{rx}, {ry}]")
else:
    print("⚠️  No ramps found in database")
    print("   Make sure you have nodes with:")
    print("   - name/id containing 'ramp'")
    print("   - type = 'ramp', 'ramp_entry', or 'ramp_exit'")
    print("   - accessible = true")

# Test stair detection
print("\n🔍 Testing STAIR detection...")
stair_blocked_cells = get_stair_blocked_cells()
if stair_blocked_cells:
    print(f"✅ Found {len(stair_blocked_cells)} blocked stair cells")
    # Show unique stair node locations (approximate)
    stair_nodes = set()
    for gx, gy in stair_blocked_cells:
        # Group nearby cells (within 10 cells) to find stair centers
        found = False
        for sx, sy in stair_nodes:
            if abs(gx - sx) < 10 and abs(gy - sy) < 10:
                found = True
                break
        if not found:
            stair_nodes.add((gx, gy))
    
    print(f"   Approximate {len(stair_nodes)} stair location(s):")
    for sx, sy in list(stair_nodes)[:10]:  # Show first 10
        print(f"   - Around grid [{sx}, {sy}]")
    if len(stair_nodes) > 10:
        print(f"   ... and {len(stair_nodes) - 10} more")
else:
    print("⚠️  No stairs found to block")
    print("   Make sure you have nodes with:")
    print("   - name/id containing 'stair' or 'step'")
    print("   - type = 'stairs', 'stairs_entry', or 'stairs_exit'")
    print("   - accessible = false")

# Test MongoDB query directly
print("\n🔍 Testing MongoDB queries directly...")
print("\n   Searching for ramp nodes:")
ramp_nodes = list(nodes_collection.find({
    "$or": [
        {"properties.name": {"$regex": "ramp", "$options": "i"}},
        {"properties.id": {"$regex": "ramp", "$options": "i"}},
        {"properties.type": {"$in": ["ramp", "ramp_entry", "ramp_exit"]}},
        {"properties.accessible": True, "properties.type": {"$ne": "stairs"}}
    ],
    "_meta.is_archived": {"$ne": True}
}))
print(f"   Found {len(ramp_nodes)} ramp node(s) in MongoDB")

print("\n   Searching for stair nodes:")
stair_nodes_db = list(nodes_collection.find({
    "$or": [
        {"properties.name": {"$regex": "stair|step", "$options": "i"}},
        {"properties.id": {"$regex": "stair|step", "$options": "i"}},
        {"properties.type": {"$in": ["stairs", "stairs_entry", "stairs_exit"]}},
        {"properties.accessible": False, "properties.type": {"$ne": "ramp"}}
    ],
    "_meta.is_archived": {"$ne": True}
}))
print(f"   Found {len(stair_nodes_db)} stair node(s) in MongoDB")

if stair_nodes_db:
    print("\n   Stair node details:")
    for node in stair_nodes_db[:5]:  # Show first 5
        props = node.get("properties", {})
        coords = node.get("geometry", {}).get("coordinates", [])
        print(f"   - {props.get('name', props.get('id', 'Unknown'))}")
        print(f"     Type: {props.get('type', 'N/A')}")
        print(f"     Accessible: {props.get('accessible', 'N/A')}")
        if coords:
            print(f"     Coordinates: [{coords[0]}, {coords[1]}]")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
if ramp_locations and stair_blocked_cells:
    print("✅ Accessibility features should work correctly!")
    print("   - Ramps detected and will be preferred")
    print("   - Stairs detected and will be blocked in accessibility mode")
elif ramp_locations:
    print("⚠️  Ramps detected, but no stairs found")
    print("   - Paths will prefer ramps, but stairs won't be blocked")
elif stair_blocked_cells:
    print("⚠️  Stairs detected, but no ramps found")
    print("   - Stairs will be blocked, but no ramp preference")
else:
    print("❌ No ramps or stairs detected")
    print("   - Accessibility mode may not work as expected")
    print("   - Check your MongoDB nodes have correct properties")

print("\n💡 TIP: Restart your backend server after adding/modifying nodes!")
print("="*60)

