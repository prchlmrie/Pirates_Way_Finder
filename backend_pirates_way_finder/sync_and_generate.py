"""
Sync frontend map (1449 x 2565) to backend and generate matching grid
"""

import shutil
from pathlib import Path
from PIL import Image
from app.services.grid_builder import generate_grid

print("=" * 60)
print("SYNC MAP AND GENERATE GRID FOR 1449 x 2565")
print("=" * 60)

# Paths
source_map = Path("../frontend_pirates_way_finder/assets/maps/map.png")
dest_map = Path("app/static/map.png")

# Step 1: Copy map
print("\n📋 Step 1: Copying resized map from frontend...")
print(f"   From: {source_map}")
print(f"   To: {dest_map}")

if not source_map.exists():
    print(f"\n❌ ERROR: Frontend map not found at: {source_map}")
    print("\nMake sure your resized map.png is in:")
    print("   frontend_pirates_way_finder/assets/maps/map.png")
    exit(1)

# Create destination directory if it doesn't exist
dest_map.parent.mkdir(parents=True, exist_ok=True)

# Copy the map
shutil.copy(source_map, dest_map)
print(f"   ✅ Map copied successfully!")

# Verify dimensions
img = Image.open(dest_map)
width, height = img.size
print(f"\n📐 Backend map dimensions: {width} x {height} pixels")

if width != 1449 or height != 2565:
    print(f"\n⚠️  WARNING: Map dimensions are not 1449 x 2565!")
    print(f"   Actual: {width} x {height}")
    print(f"   Expected: 1449 x 2565")
    print(f"\n   Continuing anyway...")
else:
    print(f"   ✅ Dimensions match! (1449 x 2565)")

# Step 2: Generate grid
print(f"\n📋 Step 2: Generating grid...")
print(f"   Cell size: 10px")
print(f"   Threshold: 80")
print()

stats = generate_grid(str(dest_map), cell_size=10, threshold=80)

print(f"\n✅ Grid generated!")
print(f"   Grid: {stats['grid_width']} x {stats['grid_height']} cells")
print(f"   Walkable: {stats['walkable_count']:,} ({stats['walkable_count']/(stats['walkable_count']+stats['wall_count'])*100:.1f}%)")
print(f"   Walls: {stats['wall_count']:,} ({stats['wall_count']/(stats['walkable_count']+stats['wall_count'])*100:.1f}%)")

print(f"\n" + "=" * 60)
print("✅ ALL DONE!")
print("=" * 60)
print(f"\n📁 Files created:")
print(f"   ✅ Backend map: app/static/map.png ({width} x {height})")
print(f"   ✅ Grid: app/static/grid.json ({stats['grid_width']} x {stats['grid_height']} cells)")
print(f"\n📋 Next step - Visualize the grid:")
print(f"   python visualize_grid.py")
print(f"\n💡 This will create grid_visualization.png showing:")
print(f"   🟢 Green = Walkable areas")
print(f"   🔴 Red = Walls/obstacles")
print(f"\n" + "=" * 60)

