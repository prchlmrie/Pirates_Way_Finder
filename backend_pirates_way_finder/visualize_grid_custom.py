"""
Custom Grid Visualization Tool
Allows you to customize colors, opacity, and cell size
"""

from PIL import Image, ImageDraw
import json

def visualize_grid_custom(
    map_path="app/static/map.png", 
    grid_path="app/static/grid.json", 
    output_path="grid_visualization.png",
    walkable_color=(0, 255, 0),      # Green (R, G, B)
    wall_color=(255, 0, 0),           # Red (R, G, B)
    walkable_opacity=40,              # 0-255 (lower = more transparent)
    wall_opacity=80,                  # 0-255 (lower = more transparent)
    show_grid_lines=False,            # Draw grid lines?
    grid_line_color=(128, 128, 128),  # Gray
    grid_line_width=1
):
    """
    Creates a customizable visual representation of the grid
    
    Parameters:
    - walkable_color: RGB tuple for walkable cells (default: green)
    - wall_color: RGB tuple for wall cells (default: red)
    - walkable_opacity: 0-255, how visible walkable cells are
    - wall_opacity: 0-255, how visible wall cells are
    - show_grid_lines: Draw cell boundaries?
    """
    
    # Load the original map
    map_img = Image.open(map_path).convert("RGB")
    
    # Load the grid
    with open(grid_path, "r") as f:
        grid_data = json.load(f)
    
    grid = grid_data["grid"]
    cell_size = grid_data["cell_size"]
    
    # Create a semi-transparent overlay
    overlay = Image.new("RGBA", map_img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    print(f"Grid dimensions: {grid_data['width']}x{grid_data['height']} cells")
    print(f"Cell size: {cell_size}x{cell_size} pixels")
    print(f"Walkable color: RGB{walkable_color} @ {walkable_opacity}/255 opacity")
    print(f"Wall color: RGB{wall_color} @ {wall_opacity}/255 opacity")
    
    wall_count = 0
    walkable_count = 0
    
    # Draw each cell
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            left = x * cell_size
            top = y * cell_size
            right = left + cell_size
            bottom = top + cell_size
            
            if grid[y][x] == 1:  # Wall
                color = wall_color + (wall_opacity,)  # Add alpha channel
                draw.rectangle([left, top, right, bottom], fill=color)
                wall_count += 1
            else:  # Walkable
                color = walkable_color + (walkable_opacity,)  # Add alpha channel
                draw.rectangle([left, top, right, bottom], fill=color)
                walkable_count += 1
            
            # Draw grid lines if requested
            if show_grid_lines:
                draw.rectangle(
                    [left, top, right, bottom], 
                    outline=grid_line_color + (128,),  # Semi-transparent
                    width=grid_line_width
                )
    
    # Combine the original map with the overlay
    map_img = map_img.convert("RGBA")
    result = Image.alpha_composite(map_img, overlay)
    
    # Save the result
    result.save(output_path)
    
    total = wall_count + walkable_count
    print(f"\n✅ Visualization saved to: {output_path}")
    print(f"\nStatistics:")
    print(f"   Walkable cells: {walkable_count:,} ({walkable_count/total*100:.1f}%)")
    print(f"   Wall cells: {wall_count:,} ({wall_count/total*100:.1f}%)")

if __name__ == "__main__":
    print("=" * 60)
    print("CUSTOM GRID VISUALIZATION TOOL")
    print("=" * 60)
    print()
    
    # Example presets
    print("Choose a preset:")
    print("  1. Default (Green walkable, Red walls)")
    print("  2. High contrast (Bright colors)")
    print("  3. Subtle (Very transparent)")
    print("  4. Blue theme (Blue walkable, Orange walls)")
    print("  5. Grid lines (Show cell boundaries)")
    print("  6. Custom (enter your own settings)")
    print()
    
    choice = input("Enter choice (1-6) or press Enter for default: ").strip()
    
    if choice == "2":  # High contrast
        visualize_grid_custom(
            walkable_color=(0, 255, 0),
            wall_color=(255, 0, 0),
            walkable_opacity=100,
            wall_opacity=150
        )
    elif choice == "3":  # Subtle
        visualize_grid_custom(
            walkable_color=(0, 255, 0),
            wall_color=(255, 0, 0),
            walkable_opacity=20,
            wall_opacity=40
        )
    elif choice == "4":  # Blue theme
        visualize_grid_custom(
            walkable_color=(0, 100, 255),    # Blue
            wall_color=(255, 140, 0),         # Orange
            walkable_opacity=50,
            wall_opacity=100
        )
    elif choice == "5":  # With grid lines
        visualize_grid_custom(
            walkable_color=(0, 255, 0),
            wall_color=(255, 0, 0),
            walkable_opacity=40,
            wall_opacity=80,
            show_grid_lines=True
        )
    elif choice == "6":  # Custom
        print("\nEnter RGB values (0-255):")
        wr = int(input("Walkable Red: "))
        wg = int(input("Walkable Green: "))
        wb = int(input("Walkable Blue: "))
        wo = int(input("Walkable Opacity (0-255): "))
        
        print("\nWall colors:")
        ar = int(input("Wall Red: "))
        ag = int(input("Wall Green: "))
        ab = int(input("Wall Blue: "))
        ao = int(input("Wall Opacity (0-255): "))
        
        visualize_grid_custom(
            walkable_color=(wr, wg, wb),
            wall_color=(ar, ag, ab),
            walkable_opacity=wo,
            wall_opacity=ao
        )
    else:  # Default
        visualize_grid_custom()
    
    print("\n✅ Done! Open 'grid_visualization.png' to see the result.")
    print("=" * 60)

