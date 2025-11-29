"""
Generate grid for the CURRENT backend map (whatever size it is)
This will automatically detect the map size and generate matching grid
"""

from app.services.grid_builder import generate_grid
from PIL import Image
from pathlib import Path

map_path = "app/static/map.png"

print("=" * 60)
print("GENERATE GRID FOR CURRENT BACKEND MAP")
print("=" * 60)

# Check if map exists
if not Path(map_path).exists():
    print(f"\n❌ ERROR: Map file not found at: {map_path}")
    print("\nMake sure:")
    print("   1. map.png is in: backend_pirates_way_finder/app/static/")
    exit(1)

# Get actual map dimensions
img = Image.open(map_path)
width, height = img.size

print(f"\n📐 Backend Map: {map_path}")
print(f"   Dimensions: {width} x {height} pixels")

# Grid settings
CELL_SIZE = 10
THRESHOLD = 80

print(f"\n📊 Grid Settings:")
print(f"   Cell Size: {CELL_SIZE} x {CELL_SIZE} pixels")
print(f"   Threshold: {THRESHOLD} (darker pixels = walls)")
print(f"   Expected Grid: {width // CELL_SIZE} x {height // CELL_SIZE} cells")

# Calculate leftover pixels (this is normal)
grid_w = width // CELL_SIZE
grid_h = height // CELL_SIZE
leftover_w = width - (grid_w * CELL_SIZE)
leftover_h = height - (grid_h * CELL_SIZE)

if leftover_w > 0 or leftover_h > 0:
    print(f"\n💡 Note: {leftover_w} x {leftover_h} pixels will be unused")
    print(f"   This is normal - grid covers {grid_w * CELL_SIZE} x {grid_h * CELL_SIZE} pixels")

print(f"\n🔄 Generating grid...")
print()

# Generate the grid
stats = generate_grid(map_path, cell_size=CELL_SIZE, threshold=THRESHOLD)

print(f"\n✅ Grid generated successfully!")
print(f"\n📐 Map: {stats['map_width']} x {stats['map_height']} pixels")
print(f"🔲 Grid: {stats['grid_width']} x {stats['grid_height']} cells")
print(f"📊 Walkable: {stats['walkable_count']:,} ({stats['walkable_count']/(stats['walkable_count']+stats['wall_count'])*100:.1f}%)")
print(f"📊 Walls: {stats['wall_count']:,} ({stats['wall_count']/(stats['walkable_count']+stats['wall_count'])*100:.1f}%)")

print(f"\n" + "=" * 60)
print("NEXT STEPS:")
print("=" * 60)
print(f"\n1. Visualize the grid:")
print(f"   python visualize_grid.py")
print(f"\n2. Check alignment:")
print(f"   python fix_map_alignment.py")
print(f"\n3. If threshold needs adjustment, regenerate:")
print(f"   python -c \"from app.services.grid_builder import generate_grid; generate_grid('app/static/map.png', cell_size=10, threshold=70)\"")
print(f"\n4. Restart backend:")
print(f"   python main.py")
print(f"\n" + "=" * 60)



