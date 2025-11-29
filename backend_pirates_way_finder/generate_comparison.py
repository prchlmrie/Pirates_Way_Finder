"""
Generate static comparison image of Dijkstra vs A* pathfinding algorithms
Perfect for documentation and presentations!
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import heapq
from app.core.grid_loader import grid_instance
from app.services.pathfinding import dijkstra
from app.services.pathfinding_astar import astar
from PIL import Image
import numpy as np

# Load grid first
print("[LOADING] Grid data...")
grid_instance.load("app/static/grid.json")
print(f"[OK] Grid loaded: {grid_instance.w}x{grid_instance.h} cells")

def get_neighbors(x, y):
    """Get walkable neighboring cells"""
    dirs = [(1,0), (-1,0), (0,1), (0,-1)]
    g = grid_instance.grid
    
    for dx, dy in dirs:
        nx = x + dx
        ny = y + dy
        if 0 <= nx < grid_instance.w and 0 <= ny < grid_instance.h:
            if g[ny][nx] == 0:  # walkable
                yield nx, ny

def manhattan_heuristic(x, y, goal_x, goal_y):
    """Manhattan distance heuristic"""
    return abs(x - goal_x) + abs(y - goal_y)

def run_dijkstra_with_visited(start, end):
    """Run Dijkstra and track visited cells"""
    pq = [(0, start)]
    dist = {start: 0}
    prev = {}
    visited = set()
    
    while pq:
        cost, (x, y) = heapq.heappop(pq)
        if (x, y) in visited:
            continue
        visited.add((x, y))
        
        if (x, y) == end:
            break
        
        for nx, ny in get_neighbors(x, y):
            new_cost = cost + 1
            if (nx, ny) not in dist or new_cost < dist[(nx, ny)]:
                dist[(nx, ny)] = new_cost
                prev[(nx, ny)] = (x, y)
                heapq.heappush(pq, (new_cost, (nx, ny)))
    
    # Reconstruct path
    path = []
    cur = end
    while cur in prev:
        path.append(cur)
        cur = prev[cur]
    path.append(start)
    path.reverse()
    
    return path, visited

def run_astar_with_visited(start, end):
    """Run A* and track visited cells"""
    sx, sy = start
    ex, ey = end
    h = manhattan_heuristic(sx, sy, ex, ey)
    pq = [(h, 0, start)]
    dist = {start: 0}
    prev = {}
    visited = set()
    
    while pq:
        f_cost, g_cost, (x, y) = heapq.heappop(pq)
        if (x, y) in visited:
            continue
        visited.add((x, y))
        
        if (x, y) == end:
            break
        
        for nx, ny in get_neighbors(x, y):
            new_g = g_cost + 1
            if (nx, ny) not in dist or new_g < dist[(nx, ny)]:
                dist[(nx, ny)] = new_g
                prev[(nx, ny)] = (x, y)
                h = manhattan_heuristic(nx, ny, ex, ey)
                f = new_g + h
                heapq.heappush(pq, (f, new_g, (nx, ny)))
    
    # Reconstruct path
    path = []
    cur = end
    while cur in prev:
        path.append(cur)
        cur = prev[cur]
    path.append(start)
    path.reverse()
    
    return path, visited

def generate_comparison_image(start_px, start_py, end_px, end_py, output_path="comparison_dijkstra_vs_astar.png"):
    """Generate side-by-side comparison image"""
    print(f"\n[PATHFINDING] Calculating paths...")
    print(f"  Start: ({start_px}, {start_py})")
    print(f"  End: ({end_px}, {end_py})")
    
    # Convert to grid coordinates
    cell_size = grid_instance.cell_size
    start_grid = (start_px // cell_size, start_py // cell_size)
    end_grid = (end_px // cell_size, end_py // cell_size)
    
    print(f"  Grid Start: {start_grid}")
    print(f"  Grid End: {end_grid}")
    
    # Run both algorithms
    print("\n[DIJKSTRA] Running algorithm...")
    dijkstra_path, dijkstra_visited = run_dijkstra_with_visited(start_grid, end_grid)
    print(f"  Visited: {len(dijkstra_visited):,} cells")
    print(f"  Path length: {len(dijkstra_path)} cells")
    
    print("\n[A*] Running algorithm...")
    astar_path, astar_visited = run_astar_with_visited(start_grid, end_grid)
    print(f"  Visited: {len(astar_visited):,} cells")
    print(f"  Path length: {len(astar_path)} cells")
    
    # Load map image
    map_img = Image.open("app/static/map.png")
    map_array = np.array(map_img)
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
    fig.suptitle('Pathfinding Algorithm Comparison: Dijkstra vs A*', 
                 fontsize=18, fontweight='bold', y=0.98)
    
    # Convert grid coordinates to pixel coordinates
    def grid_to_pixel(x, y):
        return (x * cell_size + cell_size/2, y * cell_size + cell_size/2)
    
    # Plot Dijkstra
    ax1.imshow(map_array, extent=[0, map_img.width, map_img.height, 0], alpha=0.4)
    ax1.set_xlim(0, map_img.width)
    ax1.set_ylim(map_img.height, 0)
    ax1.axis('off')
    ax1.set_title('Dijkstra\'s Algorithm', fontsize=16, fontweight='bold', color='#0066CC', pad=20)
    
    # Plot visited cells (Dijkstra)
    visited_pixels_d = [grid_to_pixel(x, y) for x, y in dijkstra_visited]
    if visited_pixels_d:
        x_coords, y_coords = zip(*visited_pixels_d)
        ax1.scatter(x_coords, y_coords, c='yellow', s=8, alpha=0.4, marker='s', 
                   label=f'Explored ({len(dijkstra_visited):,} cells)')
    
    # Plot path (Dijkstra)
    if len(dijkstra_path) > 1:
        path_pixels_d = [grid_to_pixel(x, y) for x, y in dijkstra_path]
        x_coords, y_coords = zip(*path_pixels_d)
        ax1.plot(x_coords, y_coords, 'b-', linewidth=4, label='Shortest Path', zorder=10)
    
    # Start/End markers (Dijkstra)
    start_px_coord = grid_to_pixel(*start_grid)
    end_px_coord = grid_to_pixel(*end_grid)
    ax1.scatter([start_px_coord[0]], [start_px_coord[1]], c='green', s=200, 
               marker='o', edgecolors='black', linewidths=2, label='Start', zorder=15)
    ax1.scatter([end_px_coord[0]], [end_px_coord[1]], c='red', s=200, 
               marker='s', edgecolors='black', linewidths=2, label='End', zorder=15)
    
    # Stats text (Dijkstra)
    stats_text_d = f"Cells Explored: {len(dijkstra_visited):,}\n"
    stats_text_d += f"Path Length: {len(dijkstra_path)} cells\n"
    stats_text_d += f"Algorithm: Uninformed Search\n"
    stats_text_d += f"Guarantee: Shortest Path"
    ax1.text(0.02, 0.98, stats_text_d, transform=ax1.transAxes, 
            fontsize=11, verticalalignment='top', 
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='blue', linewidth=2))
    
    ax1.legend(loc='lower right', fontsize=10)
    
    # Plot A*
    ax2.imshow(map_array, extent=[0, map_img.width, map_img.height, 0], alpha=0.4)
    ax2.set_xlim(0, map_img.width)
    ax2.set_ylim(map_img.height, 0)
    ax2.axis('off')
    ax2.set_title('A* Algorithm (Manhattan Heuristic)', fontsize=16, fontweight='bold', color='#CC0000', pad=20)
    
    # Plot visited cells (A*)
    visited_pixels_a = [grid_to_pixel(x, y) for x, y in astar_visited]
    if visited_pixels_a:
        x_coords, y_coords = zip(*visited_pixels_a)
        ax2.scatter(x_coords, y_coords, c='yellow', s=8, alpha=0.4, marker='s',
                   label=f'Explored ({len(astar_visited):,} cells)')
    
    # Plot path (A*)
    if len(astar_path) > 1:
        path_pixels_a = [grid_to_pixel(x, y) for x, y in astar_path]
        x_coords, y_coords = zip(*path_pixels_a)
        ax2.plot(x_coords, y_coords, 'r-', linewidth=4, label='Shortest Path', zorder=10)
    
    # Start/End markers (A*)
    ax2.scatter([start_px_coord[0]], [start_px_coord[1]], c='green', s=200, 
               marker='o', edgecolors='black', linewidths=2, label='Start', zorder=15)
    ax2.scatter([end_px_coord[0]], [end_px_coord[1]], c='red', s=200, 
               marker='s', edgecolors='black', linewidths=2, label='End', zorder=15)
    
    # Stats text (A*)
    stats_text_a = f"Cells Explored: {len(astar_visited):,}\n"
    stats_text_a += f"Path Length: {len(astar_path)} cells\n"
    stats_text_a += f"Algorithm: Informed Search\n"
    stats_text_a += f"Heuristic: Manhattan Distance\n"
    stats_text_a += f"Guarantee: Shortest Path (faster)"
    ax2.text(0.02, 0.98, stats_text_a, transform=ax2.transAxes, 
            fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='red', linewidth=2))
    
    ax2.legend(loc='lower right', fontsize=10)
    
    # Add algorithm explanation at the bottom
    explanation = (
        "Dijkstra: Explores uniformly in all directions. Guarantees shortest path but explores more cells.\n"
        "A*: Uses heuristic (Manhattan distance) to guide search toward goal. Guarantees shortest path with fewer explored cells."
    )
    fig.text(0.5, 0.02, explanation, ha='center', fontsize=12, 
            style='italic', color='gray')
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.93, bottom=0.08)
    
    # Save image
    print(f"\n[SAVING] Comparison image to: {output_path}")
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"[SUCCESS] Image saved!")
    
    # Show comparison stats
    print(f"\n[COMPARISON RESULTS]")
    print(f"  Dijkstra explored: {len(dijkstra_visited):,} cells")
    print(f"  A* explored: {len(astar_visited):,} cells")
    efficiency = ((len(dijkstra_visited) - len(astar_visited)) / len(dijkstra_visited)) * 100
    print(f"  A* is {efficiency:.1f}% more efficient (explored {len(dijkstra_visited) - len(astar_visited):,} fewer cells)")
    print(f"  Both found path length: {len(dijkstra_path)} cells")
    
    plt.show()
    
    return output_path

def main():
    print("=" * 70)
    print("PATHFINDING ALGORITHM COMPARISON GENERATOR")
    print("=" * 70)
    print("\nThis script generates a side-by-side comparison of Dijkstra vs A*")
    print("Perfect for documentation and presentations!\n")
    
    # Get coordinates
    print("Enter coordinates (or press Enter for defaults):")
    print("  Default Start: (671, 2453)")
    print("  Default End: (691, 692)")
    
    start_input = input("\nStart (x,y) or Enter for default: ").strip()
    if start_input:
        sx, sy = map(int, start_input.split(","))
    else:
        sx, sy = 671, 2453
    
    end_input = input("End (x,y) or Enter for default: ").strip()
    if end_input:
        ex, ey = map(int, end_input.split(","))
    else:
        ex, ey = 691, 692
    
    output_input = input("Output filename (or Enter for 'comparison_dijkstra_vs_astar.png'): ").strip()
    output_path = output_input if output_input else "comparison_dijkstra_vs_astar.png"
    
    # Generate comparison
    generate_comparison_image(sx, sy, ex, ey, output_path)
    
    print("\n" + "=" * 70)
    print("[DONE] Comparison image generated!")
    print("=" * 70)

if __name__ == "__main__":
    main()

