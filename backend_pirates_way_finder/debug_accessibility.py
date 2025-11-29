"""
Debug script to check ramp and stair detection from MongoDB
"""

from app.core.database import nodes_collection
from app.core.grid_loader import grid_instance
import json

# Load grid first
try:
    grid_instance.load("app/static/grid.json")
    print(f"✅ Grid loaded: {grid_instance.w}x{grid_instance.h} cells (cell_size: {grid_instance.cell_size}px)")
except Exception as e:
    print(f"❌ Error loading grid: {e}")
    exit(1)

print("\n" + "="*70)
print("MONGODB ACCESSIBILITY NODE CHECK")
print("="*70)

# Check all nodes with accessibility-related properties
print("\n🔍 Checking ALL nodes with accessibility info...")
print("-"*70)

# Find all nodes that might be ramps or stairs
all_accessibility_nodes = list(nodes_collection.find({
    "$or": [
        {"properties.name": {"$regex": "ramp|stair|step", "$options": "i"}},
        {"properties.id": {"$regex": "ramp|stair|step", "$options": "i"}},
        {"properties.type": {"$in": ["ramp", "ramp_entry", "ramp_exit", "stairs", "stairs_entry", "stairs_exit"]}},
        {"properties.accessible": {"$exists": True}}
    ],
    "_meta.is_archived": {"$ne": True}
}))

print(f"Found {len(all_accessibility_nodes)} accessibility-related nodes\n")

# Separate into ramps and stairs
ramps_found = []
stairs_found = []

for node in all_accessibility_nodes:
    props = node.get("properties", {})
    coords = node.get("geometry", {}).get("coordinates", [])
    
    node_id = props.get("id", "N/A")
    node_name = props.get("name", "N/A")
    node_type = props.get("type", "N/A")
    accessible = props.get("accessible", None)
    
    if coords:
        px, py = coords[0], coords[1]
        gx, gy = px // grid_instance.cell_size, py // grid_instance.cell_size
    else:
        gx, gy = None, None
    
    # Determine if it's a ramp or stair
    is_ramp = False
    is_stair = False
    
    # Check by type
    if node_type in ["ramp", "ramp_entry", "ramp_exit"]:
        is_ramp = True
    elif node_type in ["stairs", "stairs_entry", "stairs_exit"]:
        is_stair = True
    
    # Check by name/id
    name_lower = str(node_name).lower()
    id_lower = str(node_id).lower()
    if "ramp" in name_lower or "ramp" in id_lower:
        is_ramp = True
    elif "stair" in name_lower or "step" in name_lower or "stair" in id_lower or "step" in id_lower:
        is_stair = True
    
    # Check by accessible property
    if accessible is True:
        is_ramp = True
    elif accessible is False:
        is_stair = True
    
    node_info = {
        "id": node_id,
        "name": node_name,
        "type": node_type,
        "accessible": accessible,
        "pixel": [px, py] if coords else None,
        "grid": [gx, gy] if gx is not None else None
    }
    
    if is_ramp:
        ramps_found.append(node_info)
    elif is_stair:
        stairs_found.append(node_info)

# Print ramps
print("="*70)
print("RAMP NODES DETECTED")
print("="*70)
if ramps_found:
    for i, ramp in enumerate(ramps_found, 1):
        print(f"\n{i}. ID: {ramp['id']}")
        print(f"   Name: {ramp['name']}")
        print(f"   Type: {ramp['type']}")
        print(f"   Accessible: {ramp['accessible']}")
        if ramp['pixel']:
            print(f"   Pixel: [{ramp['pixel'][0]}, {ramp['pixel'][1]}]")
            print(f"   Grid: [{ramp['grid'][0]}, {ramp['grid'][1]}]")
        print()
else:
    print("❌ NO RAMP NODES FOUND!")
    print("\n   Looking for nodes with:")
    print("   - name/id containing 'ramp'")
    print("   - type = 'ramp', 'ramp_entry', or 'ramp_exit'")
    print("   - accessible = true")

# Print stairs
print("="*70)
print("STAIR NODES DETECTED")
print("="*70)
if stairs_found:
    for i, stair in enumerate(stairs_found, 1):
        print(f"\n{i}. ID: {stair['id']}")
        print(f"   Name: {stair['name']}")
        print(f"   Type: {stair['type']}")
        print(f"   Accessible: {stair['accessible']}")
        if stair['pixel']:
            print(f"   Pixel: [{stair['pixel'][0]}, {stair['pixel'][1]}]")
            print(f"   Grid: [{stair['grid'][0]}, {stair['grid'][1]}]")
        print()
else:
    print("⚠️  NO STAIR NODES FOUND!")
    print("\n   Looking for nodes with:")
    print("   - name/id containing 'stair' or 'step'")
    print("   - type = 'stairs', 'stairs_entry', or 'stairs_exit'")
    print("   - accessible = false")

# Test the actual detection functions
print("\n" + "="*70)
print("TESTING DETECTION FUNCTIONS")
print("="*70)

try:
    from app.services.pathfinding_astar import get_ramp_cells, get_stair_blocked_cells
    
    print("\n🔍 Testing get_ramp_cells()...")
    ramp_cells = get_ramp_cells()
    print(f"   Result: {len(ramp_cells)} ramp cells marked")
    if ramp_cells:
        print(f"   Sample cells: {list(ramp_cells)[:5]}")
    
    print("\n🔍 Testing get_stair_blocked_cells()...")
    stair_cells = get_stair_blocked_cells()
    print(f"   Result: {len(stair_cells)} stair cells blocked")
    if stair_cells:
        print(f"   Sample cells: {list(stair_cells)[:5]}")
    
except Exception as e:
    print(f"❌ Error testing detection functions: {e}")
    import traceback
    traceback.print_exc()

# Check for potential issues
print("\n" + "="*70)
print("POTENTIAL ISSUES")
print("="*70)

issues = []

if not ramps_found:
    issues.append("❌ No ramp nodes found in MongoDB - paths can't use ramps!")

if not stairs_found:
    issues.append("⚠️  No stair nodes found - stairs won't be blocked")

# Check if ramps have correct accessible flag
for ramp in ramps_found:
    if ramp['accessible'] is not True:
        issues.append(f"⚠️  Ramp '{ramp['id']}' has accessible={ramp['accessible']} (should be True)")

# Check if stairs have correct accessible flag
for stair in stairs_found:
    if stair['accessible'] is not False:
        issues.append(f"⚠️  Stair '{stair['id']}' has accessible={stair['accessible']} (should be False)")

if issues:
    for issue in issues:
        print(issue)
else:
    print("✅ No obvious issues detected!")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Ramps found: {len(ramps_found)}")
print(f"Stairs found: {len(stairs_found)}")
print(f"Ramp cells marked: {len(ramp_cells) if 'ramp_cells' in locals() else 'N/A'}")
print(f"Stair cells blocked: {len(stair_cells) if 'stair_cells' in locals() else 'N/A'}")

if len(ramps_found) == 0:
    print("\n❌ CRITICAL: No ramps detected! This is why paths aren't working in accessibility mode.")
    print("   Make sure your ramp nodes have:")
    print("   - accessible: true")
    print("   - type: 'ramp' OR name/id containing 'ramp'")

print("\n" + "="*70)

