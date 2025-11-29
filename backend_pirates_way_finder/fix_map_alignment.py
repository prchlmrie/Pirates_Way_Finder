"""
Helper script to check and fix map alignment issues
Checks both frontend and backend map sizes
"""

from PIL import Image
from pathlib import Path

print("=" * 60)
print("MAP ALIGNMENT CHECKER")
print("=" * 60)

# Check backend map
backend_map = Path("app/static/map.png")
frontend_map = Path("../frontend_pirates_way_finder/assets/maps/map.png")

if not backend_map.exists():
    # Try alternative path
    frontend_map = Path("../frontend_pirates_way_finder/assets/map.png")

backend_size = None
frontend_size = None

# Check backend map
if backend_map.exists():
    img = Image.open(backend_map)
    backend_size = img.size
    print(f"\n✅ Backend Map Found: app/static/map.png")
    print(f"   Dimensions: {backend_size[0]} x {backend_size[1]} pixels")
else:
    print(f"\n❌ Backend Map NOT Found: app/static/map.png")

# Check frontend map
if frontend_map.exists():
    img = Image.open(frontend_map)
    frontend_size = img.size
    print(f"\n✅ Frontend Map Found: {frontend_map}")
    print(f"   Dimensions: {frontend_size[0]} x {frontend_size[1]} pixels")
else:
    print(f"\n❌ Frontend Map NOT Found: {frontend_map}")

# Compare
print("\n" + "=" * 60)
print("COMPARISON")
print("=" * 60)

if backend_size and frontend_size:
    if backend_size == frontend_size:
        print(f"\n✅ Both maps have the SAME size!")
        print(f"   {backend_size[0]} x {backend_size[1]} pixels")
        print(f"\n✅ Everything is aligned correctly!")
    else:
        print(f"\n⚠️  MAP SIZES DON'T MATCH!")
        print(f"   Backend: {backend_size[0]} x {backend_size[1]} pixels")
        print(f"   Frontend: {frontend_size[0]} x {frontend_size[1]} pixels")
        print(f"\n   This will cause pathfinding issues!")
        print(f"\n   SOLUTION:")
        if backend_size[0] > frontend_size[0]:
            print(f"   1. Your backend map is LARGER than frontend")
            print(f"   2. Copy the FRONTEND map to backend:")
            print(f"      copy \"{frontend_map}\" \"app\\static\\map.png\"")
            print(f"   3. Regenerate grid:")
            print(f"      python -c \"from app.services.grid_builder import generate_grid; generate_grid('app/static/map.png', cell_size=10, threshold=80)\"")
        else:
            print(f"   1. Your frontend map is LARGER than backend")
            print(f"   2. Update frontend to use backend map size OR")
            print(f"   3. Copy backend map to frontend")

# Check grid if exists
grid_path = Path("app/static/grid.json")
if grid_path.exists():
    import json
    with open(grid_path, 'r') as f:
        grid_data = json.load(f)
    
    grid_w = grid_data['width']
    grid_h = grid_data['height']
    cell_size = grid_data['cell_size']
    expected_w = grid_w * cell_size
    expected_h = grid_h * cell_size
    
    print("\n" + "=" * 60)
    print("GRID INFO")
    print("=" * 60)
    print(f"\n📊 Grid: {grid_w} x {grid_h} cells")
    print(f"   Cell size: {cell_size}px")
    print(f"   Expected map: {expected_w} x {expected_h} pixels")
    
    if backend_size:
        leftover_w = backend_size[0] - expected_w
        leftover_h = backend_size[1] - expected_h
        
        if leftover_w == 0 and leftover_h == 0:
            print(f"\n✅ Grid matches backend map perfectly!")
        elif abs(leftover_w) < cell_size and abs(leftover_h) < cell_size:
            print(f"\n✅ Grid aligns with backend map (with {abs(leftover_w)}x{abs(leftover_h)} leftover pixels)")
            print(f"   This is normal - leftover pixels are ignored")
        else:
            print(f"\n⚠️  Grid doesn't match backend map!")
            print(f"   Backend map: {backend_size[0]} x {backend_size[1]}")
            print(f"   Grid expects: {expected_w} x {expected_h}")
            print(f"   Difference: {leftover_w} x {leftover_h} pixels")
            print(f"\n   SOLUTION: Regenerate grid for current map size")

print("\n" + "=" * 60)



