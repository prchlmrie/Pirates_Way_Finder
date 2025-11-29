"""
Setup Script for New Map
Generates a fresh grid.json for your new map
"""

import json
import shutil
from pathlib import Path

# New map dimensions
MAP_WIDTH = 2897
MAP_HEIGHT = 5130

# Grid settings
CELL_SIZE = 10  # 10 pixels per cell (you can change this if needed)

# Calculate grid dimensions
GRID_WIDTH = MAP_WIDTH // CELL_SIZE
GRID_HEIGHT = MAP_HEIGHT // CELL_SIZE

print("=" * 60)
print("NEW MAP SETUP")
print("=" * 60)
print(f"\n📐 Map Dimensions: {MAP_WIDTH} x {MAP_HEIGHT} pixels")
print(f"📊 Cell Size: {CELL_SIZE}x{CELL_SIZE} pixels")
print(f"🔲 Grid Dimensions: {GRID_WIDTH} x {GRID_HEIGHT} cells")
print(f"📦 Total cells: {GRID_WIDTH * GRID_HEIGHT:,}")
print()

# Ask for confirmation
print("This will:")
print("  1. Create a new grid.json file")
print("  2. ALL cells will be marked as WALKABLE (0) by default")
print("  3. You can then mark walls/obstacles using edit_grid.py")
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
print("=" * 60)
print("NEXT STEPS")
print("=" * 60)
print()
print("1. Copy your new map.png to: app/static/map.png")
print("   (Make sure it's exactly 2897 x 5130 pixels)")
print()
print("2. Mark walkable areas using edit_grid.py:")
print("   python edit_grid.py")
print()
print("3. Test the animation:")
print("   ANIMATE_INTERACTIVE.bat")
print()
print("=" * 60)

