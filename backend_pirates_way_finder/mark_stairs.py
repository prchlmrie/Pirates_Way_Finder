"""
Helper script to mark stair areas in the pathfinding system

Usage:
1. Identify stair pixel coordinates on your map image
2. Convert to grid coordinates using this script
3. Add to STAIR_AREAS in app/services/pathfinding.py
"""
import json

# Load grid info
with open("app/static/grid.json", "r") as f:
    grid_data = json.load(f)

cell_size = grid_data["cell_size"]
print("=" * 60)
print("STAIR AREA MARKING TOOL")
print("=" * 60)
print(f"Current grid: {grid_data['width']}x{grid_data['height']} cells")
print(f"Cell size: {cell_size}px")
print()
print("How to mark stairs:")
print("1. Open your map image (app/static/map.png)")
print("2. Identify the pixel coordinates of stair areas")
print("3. Convert to grid coordinates using this tool")
print("4. Add to STAIR_AREAS in app/services/pathfinding.py")
print()
print("-" * 60)

def pixel_to_grid(px, py):
    """Convert pixel coordinates to grid coordinates"""
    gx = px // cell_size
    gy = py // cell_size
    return gx, gy

def mark_stair_area():
    """Interactive tool to mark stair areas"""
    print("\n📍 Enter stair area coordinates (in PIXELS)")
    print("   (You can find these by inspecting your map image)")
    print()
    
    try:
        # Get corner coordinates
        x1 = int(input("  Top-left X (pixels): "))
        y1 = int(input("  Top-left Y (pixels): "))
        x2 = int(input("  Bottom-right X (pixels): "))
        y2 = int(input("  Bottom-right Y (pixels): "))
        
        # Convert to grid
        gx1, gy1 = pixel_to_grid(x1, y1)
        gx2, gy2 = pixel_to_grid(x2, y2)
        
        print()
        print("✅ Grid coordinates:")
        print(f"   Top-left: [{gx1}, {gy1}]")
        print(f"   Bottom-right: [{gx2}, {gy2}]")
        print()
        print("📝 Add this to STAIR_AREAS in app/services/pathfinding.py:")
        print()
        print(f"    ({gx1}, {gy1}, {gx2}, {gy2}),  # Stairs from [{x1},{y1}] to [{x2},{y2}]")
        print()
        
        # Visualize on grid
        area_cells = (abs(gx2 - gx1) + 1) * (abs(gy2 - gy1) + 1)
        print(f"📊 This area covers {area_cells} grid cells")
        
    except ValueError:
        print("❌ Invalid input. Please enter numbers only.")
    except KeyboardInterrupt:
        print("\n👋 Cancelled")

# Example usage
print("\n🎯 EXAMPLE:")
print("If you have stairs at pixel coordinates [800, 1500] to [850, 1600]:")
gx1, gy1 = pixel_to_grid(800, 1500)
gx2, gy2 = pixel_to_grid(850, 1600)
print(f"   Grid coordinates: [{gx1}, {gy1}] to [{gx2}, {gy2}]")
print(f"   Add to pathfinding.py: ({gx1}, {gy1}, {gx2}, {gy2}),")
print()
print("-" * 60)

# Interactive mode
while True:
    print()
    choice = input("Mark a stair area? (y/n): ").lower()
    if choice == 'y':
        mark_stair_area()
    else:
        break

print()
print("✅ Done! Don't forget to:")
print("   1. Update STAIR_AREAS in app/services/pathfinding.py")
print("   2. Restart the backend server")
print("   3. Toggle accessibility mode in the app to test")
print()

