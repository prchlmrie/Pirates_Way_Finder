"""
Setup Script for Resized Map (1449 x 2565)
Generates a fresh grid.json for your resized map
"""

import json
import shutil
from pathlib import Path

# Resized map dimensions (50% of original)
MAP_WIDTH = 1449
MAP_HEIGHT = 2565

# Grid settings
CELL_SIZE = 10  # 10 pixels per cell

# Calculate grid dimensions
GRID_WIDTH = MAP_WIDTH // CELL_SIZE
GRID_HEIGHT = MAP_HEIGHT // CELL_SIZE

print("=" * 60)
print("RESIZED MAP SETUP (1449 x 2565)")
print("=" * 60)
print(f"\n📐 Map Dimensions: {MAP_WIDTH} x {MAP_HEIGHT} pixels")
print(f"📊 Cell Size: {CELL_SIZE}x{CELL_SIZE} pixels")
print(f"🔲 Grid Dimensions: {GRID_WIDTH} x {GRID_HEIGHT} cells")
print(f"📦 Total cells: {GRID_WIDTH * GRID_HEIGHT:,}")
print()

# Ask for confirmation
print("This will:")
print("  1. Create a new grid.json file for the RESIZED map")
print("  2. ALL cells will be marked as WALKABLE (0) by default")
print("  3. You can then mark walls/obstacles using edit_grid.py")
print()
print("⚠️  WARNING: This will replace your current grid!")
print()

response = input("Continue? (yes/no): ").strip().lower()
if response != 'yes':
    print("❌ Cancelled")
    exit(0)

# Create a grid with all cells walkable (0)
print("\n🔄 Generating grid (all walkable)...")
grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Create the grid data
grid_data = {
    "cell_size": CELL_SIZE,
    "width": GRID_WIDTH,
    "height": GRID_HEIGHT,
    "grid": grid
}

# Backup old grid if it exists
grid_path = Path("app/static/grid.json")
if grid_path.exists():
    backup_path = Path("app/static/grid.json.backup")
    shutil.copy(grid_path, backup_path)
    print(f"💾 Backed up old grid to: {backup_path}")

# Save the new grid
with open(grid_path, "w") as f:
    json.dump(grid_data, f)

print(f"✅ New grid saved to: {grid_path}")
print()

# Show statistics
walkable = sum(row.count(0) for row in grid)
walls = sum(row.count(1) for row in grid)
total = walkable + walls

print(f"📊 Grid Statistics:")
print(f"   Walkable cells: {walkable:,} ({walkable/total*100:.1f}%)")
print(f"   Wall cells: {walls:,} ({walls/total*100:.1f}%)")
print()

print("=" * 60)
print("NEXT STEPS")
print("=" * 60)
print()
print("1. ✅ Grid created for resized map (1449 x 2565)")
print()
print("2. Mark walkable corridors using edit_grid.py:")
print("   python edit_grid.py")
print()
print("3. Visualize your grid:")
print("   python visualize_grid.py")
print()
print("4. Test pathfinding:")
print("   python test_path_endpoint.py")
print()
print("5. Restart backend to load new grid:")
print("   Ctrl+C in backend terminal")
print("   python main.py")
print()
print("=" * 60)
print()
print("✅ Grid is ready! Now mark walkable areas and test!")
print("=" * 60)



