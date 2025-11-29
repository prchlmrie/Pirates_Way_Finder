"""
Quick script to generate grid for resized map (1449 x 2565)
Uses image analysis to automatically detect walkable areas
"""

from app.services.grid_builder import generate_grid
from PIL import Image
from pathlib import Path

# Expected map dimensions
EXPECTED_WIDTH = 1449
EXPECTED_HEIGHT = 2565

# Grid settings for resized map
CELL_SIZE = 10
THRESHOLD = 80  # Adjust this if needed (lower = more walkable, higher = more walls)

map_path = "app/static/map.png"

print("=" * 60)
print("GRID GENERATION FOR RESIZED MAP")
print("=" * 60)

# Check if map exists
if not Path(map_path).exists():
    print(f"\n❌ ERROR: Map file not found at: {map_path}")
    print("\nMake sure:")
    print("   1. map.png is in: backend_pirates_way_finder/app/static/")
    print("   2. The map dimensions are: 1449 x 2565 pixels")
    exit(1)

# Check map dimensions
img = Image.open(map_path)
width, height = img.size

print(f"\n📐 Map Image: {map_path}")
print(f"   Dimensions: {width} x {height} pixels")

if width != EXPECTED_WIDTH or height != EXPECTED_HEIGHT:
    print(f"\n⚠️  WARNING: Map dimensions don't match expected size!")
    print(f"   Expected: {EXPECTED_WIDTH} x {EXPECTED_HEIGHT}")
    print(f"   Actual: {width} x {height}")
    print(f"\n   The grid will still be generated for the actual image size.")
    print(f"   But make sure your frontend ZoomableMap.js has:")
    print(f"   IMAGE_WIDTH = {width}")
    print(f"   IMAGE_HEIGHT = {height}")
    
    response = input("\nContinue anyway? (yes/no): ").strip().lower()
    if response != 'yes':
        print("❌ Cancelled")
        exit(0)
else:
    print(f"✅ Map dimensions match expected size!")

print(f"\n📊 Grid Settings:")
print(f"   Cell Size: {CELL_SIZE} x {CELL_SIZE} pixels")
print(f"   Threshold: {THRESHOLD} (darker pixels = walls)")
print(f"   Expected Grid: {width // CELL_SIZE} x {height // CELL_SIZE} cells")

print(f"\n🔄 Generating grid...")
print()

# Generate the grid
stats = generate_grid(map_path, cell_size=CELL_SIZE, threshold=THRESHOLD)

print(f"\n✅ Done! Grid generated with:")
print(f"   Grid: {stats['grid_width']} x {stats['grid_height']} cells")
print(f"   Walkable: {stats['walkable_count']:,} cells ({stats['walkable_count']/(stats['walkable_count']+stats['wall_count'])*100:.1f}%)")
print(f"   Walls: {stats['wall_count']:,} cells ({stats['wall_count']/(stats['walkable_count']+stats['wall_count'])*100:.1f}%)")



