"""
Interactive side-by-side pathfinding animation
Watch Dijkstra vs A* race in real-time!
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import heapq
import time
from app.core.grid_loader import grid_instance
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

class PathfindingAnimator:
    def __init__(self, start, end, speed='fast'):
        self.start = start
        self.end = end
        self.cell_size = grid_instance.cell_size
        
        # Speed settings
        speeds = {
            'slow': 100,      # Update every 100 steps
            'medium': 50,     # Update every 50 steps
            'fast': 20,       # Update every 20 steps
            'ultra': 1        # Update every step (very slow but detailed)
        }
        self.update_interval = speeds.get(speed, 20)
        
        # Initialize both algorithms
        self.dijkstra_state = self._init_dijkstra()
        self.astar_state = self._init_astar()
        
        # Tracking
        self.frame = 0
        self.dijkstra_done = False
        self.astar_done = False
        self.start_time = time.time()
        
        # For visualization
        self.dijkstra_visited = set()
        self.astar_visited = set()
        
        print(f"[READY] Animation initialized")
        print(f"[INFO] Update interval: {self.update_interval} steps per frame")
    
    def _init_dijkstra(self):
        """Initialize Dijkstra's algorithm state"""
        pq = [(0, self.start)]
        dist = {self.start: 0}
        prev = {}
        visited = set()
        return {
            'pq': pq,
            'dist': dist,
            'prev': prev,
            'visited': visited,
            'steps': 0,
            'found': False
        }
    
    def _init_astar(self):
        """Initialize A* algorithm state"""
        sx, sy = self.start
        ex, ey = self.end
        h = manhattan_heuristic(sx, sy, ex, ey)
        pq = [(h, 0, self.start)]
        dist = {self.start: 0}
        prev = {}
        visited = set()
        return {
            'pq': pq,
            'dist': dist,
            'prev': prev,
            'visited': visited,
            'steps': 0,
            'found': False
        }
    
    def step_dijkstra(self):
        """Execute one step of Dijkstra"""
        state = self.dijkstra_state
        
        if not state['pq'] or state['found']:
            return False
        
        cost, (x, y) = heapq.heappop(state['pq'])
        
        if (x, y) in state['visited']:
            return True
        
        state['visited'].add((x, y))
        state['steps'] += 1
        
        if (x, y) == self.end:
            state['found'] = True
            self.dijkstra_done = True
            return False
        
        for nx, ny in get_neighbors(x, y):
            new_cost = cost + 1
            if (nx, ny) not in state['dist'] or new_cost < state['dist'][(nx, ny)]:
                state['dist'][(nx, ny)] = new_cost
                state['prev'][(nx, ny)] = (x, y)
                heapq.heappush(state['pq'], (new_cost, (nx, ny)))
        
        return True
    
    def step_astar(self):
        """Execute one step of A*"""
        state = self.astar_state
        
        if not state['pq'] or state['found']:
            return False
        
        f_cost, g_cost, (x, y) = heapq.heappop(state['pq'])
        
        if (x, y) in state['visited']:
            return True
        
        state['visited'].add((x, y))
        state['steps'] += 1
        
        if (x, y) == self.end:
            state['found'] = True
            self.astar_done = True
            return False
        
        ex, ey = self.end
        for nx, ny in get_neighbors(x, y):
            new_g = g_cost + 1
            
            if (nx, ny) not in state['dist'] or new_g < state['dist'][(nx, ny)]:
                state['dist'][(nx, ny)] = new_g
                state['prev'][(nx, ny)] = (x, y)
                
                h = manhattan_heuristic(nx, ny, ex, ey)
                f = new_g + h
                heapq.heappush(state['pq'], (f, new_g, (nx, ny)))
        
        return True
    
    def get_path(self, state):
        """Reconstruct path from algorithm state"""
        if not state['found']:
            return []
        
        path = []
        cur = self.end
        while cur in state['prev']:
            path.append(cur)
            cur = state['prev'][cur]
        path.append(self.start)
        path.reverse()
        return path
    
    def animate(self):
        """Run the animation"""
        # Load map image for background
        map_img = Image.open("app/static/map.png")
        map_array = np.array(map_img)
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle('Pathfinding Algorithm Race: Dijkstra vs A*', fontsize=16, fontweight='bold')
        
        # Setup both axes
        for ax in [ax1, ax2]:
            ax.imshow(map_array, extent=[0, map_img.width, map_img.height, 0], alpha=0.3)
            ax.set_xlim(0, map_img.width)
            ax.set_ylim(map_img.height, 0)
            ax.axis('off')
        
        ax1.set_title('Dijkstra', fontsize=14, fontweight='bold', color='blue')
        ax2.set_title('A* (Manhattan)', fontsize=14, fontweight='bold', color='red')
        
        # Initialize scatter plots for visited cells
        dijkstra_scatter = ax1.scatter([], [], c='yellow', s=10, alpha=0.3, marker='s')
        astar_scatter = ax2.scatter([], [], c='yellow', s=10, alpha=0.3, marker='s')
        
        # Initialize path lines
        dijkstra_path_line, = ax1.plot([], [], 'b-', linewidth=3, label='Path')
        astar_path_line, = ax2.plot([], [], 'r-', linewidth=3, label='Path')
        
        # Start/End markers
        start_px = (self.start[0] * self.cell_size + self.cell_size/2,
                   self.start[1] * self.cell_size + self.cell_size/2)
        end_px = (self.end[0] * self.cell_size + self.cell_size/2,
                 self.end[1] * self.cell_size + self.cell_size/2)
        
        for ax in [ax1, ax2]:
            # Start marker
            circle = patches.Circle(start_px, 30, color='green', zorder=10)
            ax.add_patch(circle)
            # End marker
            circle = patches.Circle(end_px, 30, color='red', zorder=10)
            ax.add_patch(circle)
        
        # Stats text
        stats_dijkstra = ax1.text(0.02, 0.98, '', transform=ax1.transAxes,
                                 verticalalignment='top', fontsize=10,
                                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        stats_astar = ax2.text(0.02, 0.98, '', transform=ax2.transAxes,
                              verticalalignment='top', fontsize=10,
                              bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        def update(frame):
            """Update function for animation"""
            self.frame = frame
            
            # Step both algorithms multiple times per frame
            for _ in range(self.update_interval):
                if not self.dijkstra_done:
                    if not self.step_dijkstra():
                        self.dijkstra_done = True
                
                if not self.astar_done:
                    if not self.step_astar():
                        self.astar_done = True
            
            # Update Dijkstra visualization
            if self.dijkstra_state['visited']:
                visited_coords = np.array([
                    (x * self.cell_size + self.cell_size/2,
                     y * self.cell_size + self.cell_size/2)
                    for x, y in self.dijkstra_state['visited']
                ])
                dijkstra_scatter.set_offsets(visited_coords)
            
            # Update A* visualization
            if self.astar_state['visited']:
                visited_coords = np.array([
                    (x * self.cell_size + self.cell_size/2,
                     y * self.cell_size + self.cell_size/2)
                    for x, y in self.astar_state['visited']
                ])
                astar_scatter.set_offsets(visited_coords)
            
            # Update paths if found
            if self.dijkstra_done:
                path = self.get_path(self.dijkstra_state)
                if path:
                    path_coords = np.array([
                        (x * self.cell_size + self.cell_size/2,
                         y * self.cell_size + self.cell_size/2)
                        for x, y in path
                    ])
                    dijkstra_path_line.set_data(path_coords[:, 0], path_coords[:, 1])
            
            if self.astar_done:
                path = self.get_path(self.astar_state)
                if path:
                    path_coords = np.array([
                        (x * self.cell_size + self.cell_size/2,
                         y * self.cell_size + self.cell_size/2)
                        for x, y in path
                    ])
                    astar_path_line.set_data(path_coords[:, 0], path_coords[:, 1])
            
            # Update stats
            dijkstra_path = self.get_path(self.dijkstra_state)
            dijkstra_text = f"Dijkstra\n"
            dijkstra_text += f"Steps: {self.dijkstra_state['steps']:,}\n"
            dijkstra_text += f"Explored: {len(self.dijkstra_state['visited']):,}\n"
            if self.dijkstra_done:
                dijkstra_text += f"Path: {len(dijkstra_path)} cells\n"
                dijkstra_text += f"✓ FOUND!"
            else:
                dijkstra_text += f"Status: Searching..."
            stats_dijkstra.set_text(dijkstra_text)
            
            astar_path = self.get_path(self.astar_state)
            astar_text = f"A*\n"
            astar_text += f"Steps: {self.astar_state['steps']:,}\n"
            astar_text += f"Explored: {len(self.astar_state['visited']):,}\n"
            if self.astar_done:
                astar_text += f"Path: {len(astar_path)} cells\n"
                astar_text += f"✓ FOUND!"
            else:
                astar_text += f"Status: Searching..."
            stats_astar.set_text(astar_text)
            
            # Stop animation when both are done
            if self.dijkstra_done and self.astar_done:
                print(f"\n[COMPLETE] Both algorithms finished!")
                print(f"[DIJKSTRA] Explored {len(self.dijkstra_state['visited']):,} cells, Path: {len(dijkstra_path)}")
                print(f"[A*] Explored {len(self.astar_state['visited']):,} cells, Path: {len(astar_path)}")
                
                if len(dijkstra_path) == len(astar_path):
                    print(f"[SUCCESS] Both found SAME shortest path!")
                else:
                    print(f"[WARNING] Different path lengths!")
                
                # Keep showing for a bit
                if frame > self.frame + 10:
                    plt.close()
            
            return dijkstra_scatter, astar_scatter, dijkstra_path_line, astar_path_line, stats_dijkstra, stats_astar
        
        # Create animation
        print(f"\n[STARTING] Animation...")
        print(f"[TIP] Close the window when you're done watching!")
        anim = FuncAnimation(fig, update, frames=range(10000), 
                           interval=50, blit=True, repeat=False)
        
        plt.tight_layout()
        plt.show()
        
        return anim

def main():
    print("=" * 60)
    print("INTERACTIVE PATHFINDING RACE ANIMATION")
    print("=" * 60)
    print("\nWatch Dijkstra vs A* race side-by-side!")
    print("Yellow = Explored cells")
    print("Blue/Red line = Shortest path")
    print("\nSpeed options:")
    print("  ultra  - Update every step (VERY detailed, slow)")
    print("  slow   - Update every 100 steps")
    print("  medium - Update every 50 steps")
    print("  fast   - Update every 20 steps (recommended)")
    
    # Get coordinates
    print("\nEnter coordinates (or press Enter for defaults):")
    print("  Start: (671, 2453)")
    print("  End: (691, 692)")
    
    start_input = input("\nStart (x,y) or Enter: ").strip()
    if start_input:
        sx, sy = map(int, start_input.split(","))
    else:
        sx, sy = 671, 2453
    
    end_input = input("End (x,y) or Enter: ").strip()
    if end_input:
        ex, ey = map(int, end_input.split(","))
    else:
        ex, ey = 691, 692
    
    speed_input = input("Speed (ultra/slow/medium/fast) or Enter: ").strip().lower()
    if speed_input not in ['ultra', 'slow', 'medium', 'fast']:
        speed_input = 'fast'
    
    # Convert to grid coordinates
    cell_size = grid_instance.cell_size
    start_grid = (sx // cell_size, sy // cell_size)
    end_grid = (ex // cell_size, ey // cell_size)
    
    print(f"\n[CONFIG]")
    print(f"  Start: pixel ({sx}, {sy}) -> grid {start_grid}")
    print(f"  End:   pixel ({ex}, {ey}) -> grid {end_grid}")
    print(f"  Speed: {speed_input}")
    
    # Create and run animation
    animator = PathfindingAnimator(start_grid, end_grid, speed=speed_input)
    animator.animate()
    
    print("\n[DONE] Animation window closed")
    print("=" * 60)

if __name__ == "__main__":
    main()

