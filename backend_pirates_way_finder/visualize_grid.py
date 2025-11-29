"""
Grid Visualization Tool
Shows the walkable grid overlaid on your map image
- Green = Walkable (0)
- Red = Wall (1)
- Orange = Stair cells (blocked in accessibility mode)
- Blue = Ramp cells (preferred in accessibility mode)
"""

from PIL import Image, ImageDraw
import json
import sys
import os

# Add the app directory to the path so we can import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def visualize_grid(map_path="app/static/map.png", grid_path="app/static/grid.json", output_path="grid_visualization.png", show_accessibility=True):
    """
    Creates a visual representation of the grid overlaid on the map
    - Green = Walkable (0)
    - Red = Wall (1)
    - Orange = Stair cells (blocked in accessibility mode)
    - Blue = Ramp cells (preferred in accessibility mode)
    """
    
    # Load the original map
    map_img = Image.open(map_path).convert("RGB")
    map_width, map_height = map_img.size
    
    # Load the grid
    with open(grid_path, "r") as f:
        grid_data = json.load(f)
    
    grid = grid_data["grid"]
    cell_size = grid_data["cell_size"]
    grid_w = grid_data["width"]
    grid_h = grid_data["height"]
    
    # Load accessibility data (stairs and ramps) if requested
    stair_blocked_cells = set()
    ramp_cells = set()
    
    if show_accessibility:
        try:
            # Import the grid loader and pathfinding functions
            from app.core.grid_loader import grid_instance
            from app.services.pathfinding_astar import get_stair_blocked_cells, get_ramp_cells
            
            # Load grid instance (required for detection functions)
            grid_instance.load(grid_path)
            
            # Get stair and ramp cells
            print("\n🔍 Loading accessibility data...")
            stair_blocked_cells = get_stair_blocked_cells()
            ramp_cells = get_ramp_cells()
            
            print(f"   ✅ Found {len(stair_blocked_cells)} stair cells")
            print(f"   ✅ Found {len(ramp_cells)} ramp cells")
        except Exception as e:
            print(f"\n⚠️  Could not load accessibility data: {e}")
            print("   Visualization will continue without stair/ramp colors")
            show_accessibility = False
    
    # Verify dimensions match
    expected_map_w = grid_w * cell_size
    expected_map_h = grid_h * cell_size
    
    print("=" * 60)
    print("GRID VISUALIZATION")
    print("=" * 60)
    print(f"\n📐 Map Image: {map_path}")
    print(f"   Dimensions: {map_width} x {map_height} pixels")
    print(f"\n🔲 Grid Data:")
    print(f"   Dimensions: {grid_w} x {grid_h} cells")
    print(f"   Cell size: {cell_size} x {cell_size} pixels")
    print(f"   Expected map size: {expected_map_w} x {expected_map_h} pixels")
    
    # Check for leftover pixels (this is normal when map size doesn't divide evenly by cell_size)
    leftover_w = map_width - expected_map_w
    leftover_h = map_height - expected_map_h
    
    if map_width != expected_map_w or map_height != expected_map_h:
        if leftover_w < cell_size and leftover_h < cell_size:
            print(f"\n✅ Dimensions align (with {leftover_w}x{leftover_h} leftover pixels - this is normal!)")
            print(f"   The last {leftover_w} pixels width and {leftover_h} pixels height")
            print(f"   will not have grid overlay, but this won't affect pathfinding.")
        else:
            print(f"\n⚠️  WARNING: Map dimensions don't match grid expectations!")
            print(f"   This may cause misalignment in visualization.")
            print(f"   Map: {map_width} x {map_height}")
            print(f"   Expected from grid: {expected_map_w} x {expected_map_h}")
            print(f"   Difference: {leftover_w} x {leftover_h} pixels")
            print(f"\n   Make sure the grid was generated from this exact map image!")
    else:
        print(f"\n✅ Dimensions match perfectly!")
    
    # Create a semi-transparent overlay
    overlay = Image.new("RGBA", map_img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    wall_count = 0
    walkable_count = 0
    stair_count = 0
    ramp_count = 0
    
    # Draw each cell
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            left = x * cell_size
            top = y * cell_size
            right = left + cell_size
            bottom = top + cell_size
            
            # Check accessibility overlays first (they take priority for visualization)
            if show_accessibility and (x, y) in stair_blocked_cells:
                # Draw orange for stair cells (blocked in accessibility mode)
                draw.rectangle([left, top, right, bottom], fill=(255, 165, 0, 120))  # Orange, more opaque
                stair_count += 1
            elif show_accessibility and (x, y) in ramp_cells:
                # Draw blue for ramp cells (preferred in accessibility mode)
                draw.rectangle([left, top, right, bottom], fill=(0, 100, 255, 100))  # Blue, semi-transparent
                ramp_count += 1
            elif grid[y][x] == 1:  # Wall
                # Draw red semi-transparent rectangle
                draw.rectangle([left, top, right, bottom], fill=(255, 0, 0, 80))
                wall_count += 1
            else:  # Walkable
                # Draw green semi-transparent rectangle
                draw.rectangle([left, top, right, bottom], fill=(0, 255, 0, 40))
                walkable_count += 1
    
    # Combine the original map with the overlay
    map_img = map_img.convert("RGBA")
    result = Image.alpha_composite(map_img, overlay)
    
    # Save the result
    result.save(output_path)
    
    total = wall_count + walkable_count
    print(f"\n✅ Visualization saved to: {output_path}")
    print(f"\n📊 Statistics:")
    print(f"   🟢 Walkable cells: {walkable_count:,} ({walkable_count/total*100:.1f}%)")
    print(f"   🔴 Wall cells: {wall_count:,} ({wall_count/total*100:.1f}%)")
    if show_accessibility:
        print(f"\n♿ Accessibility Overlays:")
        print(f"   🟠 Stair cells (blocked): {stair_count:,} (overlay on walkable cells)")
        print(f"   🔵 Ramp cells (preferred): {ramp_count:,} (overlay on walkable cells)")
    print(f"\n🎨 Colors:")
    print(f"   🟢 Green = Walkable (0)")
    print(f"   🔴 Red = Wall (1)")
    if show_accessibility:
        print(f"   🟠 Orange = Stair cells (blocked in accessibility mode)")
        print(f"   🔵 Blue = Ramp cells (preferred in accessibility mode)")
    print(f"\n💡 Tip: Open {output_path} to see the overlay on your map!")
    print("=" * 60)

def show_grid_as_text(grid_path="app/static/grid.json", rows=20, cols=40):
    """
    Shows a text representation of a portion of the grid
    """
    with open(grid_path, "r") as f:
        grid_data = json.load(f)
    
    grid = grid_data["grid"]
    
    print(f"\nGrid Preview (first {rows}x{cols} cells):")
    print("   0 = Walkable (light), 1 = Wall (dark)")
    print("   " + "".join([str(i%10) for i in range(min(cols, len(grid[0])))]))
    
    for y in range(min(rows, len(grid))):
        row_str = f"{y:2d} "
        for x in range(min(cols, len(grid[y]))):
            if grid[y][x] == 1:
                row_str += "#"  # Wall
            else:
                row_str += "."  # Walkable
        print(row_str)

if __name__ == "__main__":
    print("=== Grid Visualization Tool ===\n")
    
    # Create visual overlay
    visualize_grid()
    
    # Show text preview
    show_grid_as_text()
    
    print("\nDone! Open 'grid_visualization.png' to see the result.")

