from PIL import Image
import json
import shutil
from pathlib import Path

def generate_grid(image_path, cell_size=20, threshold=100):
    """
    Generate a walkable grid from a map image.
    
    Args:
        image_path: Path to the map image
        cell_size: Size of each grid cell in pixels (default: 20)
        threshold: Pixel darkness threshold (0-255). 
                   Pixels darker than threshold = walls (1)
                   Pixels lighter than threshold = walkable (0)
    
    Returns:
        Dictionary with grid statistics
    """
    print("=" * 60)
    print("GENERATING GRID FROM MAP IMAGE")
    print("=" * 60)
    
    # Load image
    img = Image.open(image_path).convert("L")  # grayscale
    width, height = img.size
    
    print(f"\n📐 Map Image Dimensions: {width} x {height} pixels")
    print(f"📊 Cell Size: {cell_size} x {cell_size} pixels")
    
    # Calculate grid dimensions
    grid_w = width // cell_size
    grid_h = height // cell_size
    
    print(f"🔲 Grid Dimensions: {grid_w} x {grid_h} cells")
    print(f"📦 Total cells: {grid_w * grid_h:,}")
    print(f"🎚️  Threshold: {threshold} (darker = walls)")
    print()
    
    # Backup old grid if it exists
    grid_path = Path("app/static/grid.json")
    if grid_path.exists():
        backup_path = Path("app/static/grid.json.backup")
        shutil.copy(grid_path, backup_path)
        print(f"💾 Backed up old grid to: {backup_path}")
    
    print("🔄 Analyzing map image...")
    
    grid = []
    wall_count = 0
    walkable_count = 0
    
    for y in range(grid_h):
        row = []
        for x in range(grid_w):
            # crop a cell
            left = x * cell_size
            top = y * cell_size
            right = left + cell_size
            bottom = top + cell_size
            
            cell = img.crop((left, top, right, bottom))
            
            # calculate average darkness (0 = black, 255 = white)
            avg_pixel = sum(cell.getdata()) / (cell_size * cell_size)
            
            # 0 = walkable, 1 = wall
            # Darker areas (lower avg_pixel) = walls
            # Brighter areas (higher avg_pixel) = walkable
            if avg_pixel < threshold:
                row.append(1)  # wall (dark)
                wall_count += 1
            else:
                row.append(0)  # walkable (light)
                walkable_count += 1
        
        grid.append(row)
        
        # Progress indicator
        if (y + 1) % 50 == 0 or y == grid_h - 1:
            progress = ((y + 1) / grid_h) * 100
            print(f"   Progress: {progress:.1f}% ({y+1}/{grid_h} rows)", end='\r')
    
    print("\n")
    
    # Save grid
    out = {
        "cell_size": cell_size,
        "width": grid_w,
        "height": grid_h,
        "grid": grid
    }
    
    with open("app/static/grid.json", "w") as f:
        json.dump(out, f)
    
    # Statistics
    total = wall_count + walkable_count
    wall_pct = (wall_count / total) * 100
    walkable_pct = (walkable_count / total) * 100
    
    print("=" * 60)
    print("✅ GRID GENERATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\n📊 Statistics:")
    print(f"   🟢 Walkable cells: {walkable_count:,} ({walkable_pct:.1f}%)")
    print(f"   🔴 Wall cells: {wall_count:,} ({wall_pct:.1f}%)")
    print(f"\n💾 Saved to: app/static/grid.json")
    print(f"\n🔲 Grid dimensions: {grid_w} x {grid_h} cells")
    print(f"   Map dimensions: {width} x {height} pixels")
    print(f"   Cell size: {cell_size} x {cell_size} pixels")
    print()
    print("=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("\n1. Visualize the grid:")
    print("   python visualize_grid.py")
    print()
    print("2. If threshold needs adjustment:")
    print("   python -c \"from app.services.grid_builder import generate_grid; generate_grid('app/static/map.png', cell_size=10, threshold=70)\"")
    print("   (Try different thresholds: 60, 70, 80, 90, 100)")
    print()
    print("3. Restart backend to load new grid:")
    print("   python main.py")
    print()
    print("=" * 60)
    
    return {
        "grid_width": grid_w,
        "grid_height": grid_h,
        "map_width": width,
        "map_height": height,
        "cell_size": cell_size,
        "walkable_count": walkable_count,
        "wall_count": wall_count,
        "threshold": threshold
    }