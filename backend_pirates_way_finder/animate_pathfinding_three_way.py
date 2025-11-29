"""
Interactive three-way pathfinding animation
Watch A* vs Greedy Best First vs BFS race in real-time!
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import heapq
from collections import deque
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

class ThreeWayPathfindingAnimator:
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
        
        # Initialize all three algorithms
        self.astar_state = self._init_astar()
        self.greedy_state = self._init_greedy()
        self.bfs_state = self._init_bfs()
        
        # Tracking
        self.frame = 0
        self.astar_done = False
        self.greedy_done = False
        self.bfs_done = False
        self.start_time = time.time()
        
        print(f"[READY] Animation initialized")
        print(f"[INFO] Update interval: {self.update_interval} steps per frame")
    
    def _init_astar(self):
        """Initialize A* algorithm state (f = g + h)"""
        sx, sy = self.start
        ex, ey = self.end
        h = manhattan_heuristic(sx, sy, ex, ey)
        pq = [(h, 0, self.start)]  # (f_cost, g_cost, node)
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
    
    def _init_greedy(self):
        """Initialize Greedy Best First Search state (f = h only, ignores g)"""
        sx, sy = self.start
        ex, ey = self.end
        h = manhattan_heuristic(sx, sy, ex, ey)
        pq = [(h, self.start)]  # (h_cost only, node)
        prev = {}
        visited = set()
        return {
            'pq': pq,
            'prev': prev,
            'visited': visited,
            'steps': 0,
            'found': False
        }
    
    def _init_bfs(self):
        """Initialize BFS state (FIFO queue)"""
        queue = deque([self.start])
        prev = {}
        visited = set()
        return {
            'queue': queue,
            'prev': prev,
            'visited': visited,
            'steps': 0,
            'found': False
        }
    
    def step_astar(self):
        """Execute one step of A* (f = g + h)"""
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
    
    def step_greedy(self):
        """Execute one step of Greedy Best First (f = h only)"""
        state = self.greedy_state
        
        if not state['pq'] or state['found']:
            return False
        
        h_cost, (x, y) = heapq.heappop(state['pq'])
        
        if (x, y) in state['visited']:
            return True
        
        state['visited'].add((x, y))
        state['steps'] += 1
        
        if (x, y) == self.end:
            state['found'] = True
            self.greedy_done = True
            return False
        
        ex, ey = self.end
        for nx, ny in get_neighbors(x, y):
            if (nx, ny) not in state['visited']:
                state['prev'][(nx, ny)] = (x, y)
                h = manhattan_heuristic(nx, ny, ex, ey)
                heapq.heappush(state['pq'], (h, (nx, ny)))
        
        return True
    
    def step_bfs(self):
        """Execute one step of BFS (FIFO queue)"""
        state = self.bfs_state
        
        if not state['queue'] or state['found']:
            return False
        
        (x, y) = state['queue'].popleft()
        
        # Skip if already visited (can happen if added multiple times)
        if (x, y) in state['visited']:
            return True
        
        state['visited'].add((x, y))
        state['steps'] += 1
        
        if (x, y) == self.end:
            state['found'] = True
            self.bfs_done = True
            return False
        
        # Add unvisited neighbors to queue
        for nx, ny in get_neighbors(x, y):
            if (nx, ny) not in state['visited']:
                # Check if already in queue (to avoid duplicates)
                if (nx, ny) not in state['queue']:
                    state['prev'][(nx, ny)] = (x, y)
                    state['queue'].append((nx, ny))
        
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
        
        # Create figure with three subplots
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 7))
        fig.suptitle('Pathfinding Algorithm Race: A* vs Greedy Best First vs BFS', 
                     fontsize=16, fontweight='bold')
        
        # Setup all three axes
        for ax in [ax1, ax2, ax3]:
            ax.imshow(map_array, extent=[0, map_img.width, map_img.height, 0], alpha=0.3)
            ax.set_xlim(0, map_img.width)
            ax.set_ylim(map_img.height, 0)
            ax.axis('off')
        
        ax1.set_title('A* (f = g + h)', fontsize=14, fontweight='bold', color='blue')
        ax2.set_title('Greedy Best First (f = h)', fontsize=14, fontweight='bold', color='orange')
        ax3.set_title('BFS (FIFO Queue)', fontsize=14, fontweight='bold', color='purple')
        
        # Initialize scatter plots for visited cells
        astar_scatter = ax1.scatter([], [], c='yellow', s=10, alpha=0.3, marker='s')
        greedy_scatter = ax2.scatter([], [], c='yellow', s=10, alpha=0.3, marker='s')
        bfs_scatter = ax3.scatter([], [], c='yellow', s=10, alpha=0.3, marker='s')
        
        # Initialize path lines
        astar_path_line, = ax1.plot([], [], 'b-', linewidth=3, label='Path')
        greedy_path_line, = ax2.plot([], [], 'orange', linewidth=3, label='Path')
        bfs_path_line, = ax3.plot([], [], 'purple', linewidth=3, label='Path')
        
        # Start/End markers
        start_px = (self.start[0] * self.cell_size + self.cell_size/2,
                   self.start[1] * self.cell_size + self.cell_size/2)
        end_px = (self.end[0] * self.cell_size + self.cell_size/2,
                 self.end[1] * self.cell_size + self.cell_size/2)
        
        for ax in [ax1, ax2, ax3]:
            # Start marker
            circle = patches.Circle(start_px, 30, color='green', zorder=10)
            ax.add_patch(circle)
            # End marker
            circle = patches.Circle(end_px, 30, color='red', zorder=10)
            ax.add_patch(circle)
        
        # Stats text
        stats_astar = ax1.text(0.02, 0.98, '', transform=ax1.transAxes,
                              verticalalignment='top', fontsize=9,
                              bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        stats_greedy = ax2.text(0.02, 0.98, '', transform=ax2.transAxes,
                               verticalalignment='top', fontsize=9,
                               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        stats_bfs = ax3.text(0.02, 0.98, '', transform=ax3.transAxes,
                             verticalalignment='top', fontsize=9,
                             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        def update(frame):
            """Update function for animation"""
            self.frame = frame
            
            # Step all three algorithms multiple times per frame
            for _ in range(self.update_interval):
                if not self.astar_done:
                    if not self.step_astar():
                        self.astar_done = True
                
                if not self.greedy_done:
                    if not self.step_greedy():
                        self.greedy_done = True
                
                if not self.bfs_done:
                    if not self.step_bfs():
                        self.bfs_done = True
            
            # Update A* visualization
            if self.astar_state['visited']:
                visited_coords = np.array([
                    (x * self.cell_size + self.cell_size/2,
                     y * self.cell_size + self.cell_size/2)
                    for x, y in self.astar_state['visited']
                ])
                astar_scatter.set_offsets(visited_coords)
            
            # Update Greedy visualization
            if self.greedy_state['visited']:
                visited_coords = np.array([
                    (x * self.cell_size + self.cell_size/2,
                     y * self.cell_size + self.cell_size/2)
                    for x, y in self.greedy_state['visited']
                ])
                greedy_scatter.set_offsets(visited_coords)
            
            # Update BFS visualization
            if self.bfs_state['visited']:
                visited_coords = np.array([
                    (x * self.cell_size + self.cell_size/2,
                     y * self.cell_size + self.cell_size/2)
                    for x, y in self.bfs_state['visited']
                ])
                bfs_scatter.set_offsets(visited_coords)
            
            # Update paths if found
            if self.astar_done:
                path = self.get_path(self.astar_state)
                if path:
                    path_coords = np.array([
                        (x * self.cell_size + self.cell_size/2,
                         y * self.cell_size + self.cell_size/2)
                        for x, y in path
                    ])
                    astar_path_line.set_data(path_coords[:, 0], path_coords[:, 1])
            
            if self.greedy_done:
                path = self.get_path(self.greedy_state)
                if path:
                    path_coords = np.array([
                        (x * self.cell_size + self.cell_size/2,
                         y * self.cell_size + self.cell_size/2)
                        for x, y in path
                    ])
                    greedy_path_line.set_data(path_coords[:, 0], path_coords[:, 1])
            
            if self.bfs_done:
                path = self.get_path(self.bfs_state)
                if path:
                    path_coords = np.array([
                        (x * self.cell_size + self.cell_size/2,
                         y * self.cell_size + self.cell_size/2)
                        for x, y in path
                    ])
                    bfs_path_line.set_data(path_coords[:, 0], path_coords[:, 1])
            
            # Update stats
            astar_path = self.get_path(self.astar_state)
            astar_text = f"A* (Optimal)\n"
            astar_text += f"Steps: {self.astar_state['steps']:,}\n"
            astar_text += f"Explored: {len(self.astar_state['visited']):,}\n"
            if self.astar_done:
                astar_text += f"Path: {len(astar_path)} cells\n"
                astar_text += f"✓ FOUND!"
            else:
                astar_text += f"Status: Searching..."
            stats_astar.set_text(astar_text)
            
            greedy_path = self.get_path(self.greedy_state)
            greedy_text = f"Greedy Best First\n"
            greedy_text += f"Steps: {self.greedy_state['steps']:,}\n"
            greedy_text += f"Explored: {len(self.greedy_state['visited']):,}\n"
            if self.greedy_done:
                greedy_text += f"Path: {len(greedy_path)} cells\n"
                greedy_text += f"✓ FOUND!"
                if len(greedy_path) != len(astar_path) and self.astar_done:
                    greedy_text += f"\n⚠ Not optimal!"
            else:
                greedy_text += f"Status: Searching..."
            stats_greedy.set_text(greedy_text)
            
            bfs_path = self.get_path(self.bfs_state)
            bfs_text = f"BFS (Optimal)\n"
            bfs_text += f"Steps: {self.bfs_state['steps']:,}\n"
            bfs_text += f"Explored: {len(self.bfs_state['visited']):,}\n"
            if self.bfs_done:
                bfs_text += f"Path: {len(bfs_path)} cells\n"
                bfs_text += f"✓ FOUND!"
            else:
                bfs_text += f"Status: Searching..."
            stats_bfs.set_text(bfs_text)
            
            # Stop animation when all are done
            if self.astar_done and self.greedy_done and self.bfs_done:
                print(f"\n[COMPLETE] All algorithms finished!")
                print(f"[A*] Explored {len(self.astar_state['visited']):,} cells, Path: {len(astar_path)}")
                print(f"[Greedy] Explored {len(self.greedy_state['visited']):,} cells, Path: {len(greedy_path)}")
                print(f"[BFS] Explored {len(self.bfs_state['visited']):,} cells, Path: {len(bfs_path)}")
                
                if len(astar_path) == len(bfs_path):
                    print(f"[SUCCESS] A* and BFS found SAME shortest path!")
                else:
                    print(f"[WARNING] A* and BFS path lengths differ!")
                
                if len(greedy_path) != len(astar_path):
                    print(f"[NOTE] Greedy found different path (may not be optimal)")
                else:
                    print(f"[NOTE] Greedy found same path length (lucky!)")
                
                # Keep showing for a bit
                if frame > self.frame + 10:
                    plt.close()
            
            return (astar_scatter, greedy_scatter, bfs_scatter, 
                   astar_path_line, greedy_path_line, bfs_path_line,
                   stats_astar, stats_greedy, stats_bfs)
        
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
    print("INTERACTIVE THREE-WAY PATHFINDING RACE ANIMATION")
    print("=" * 60)
    print("\nWatch A* vs Greedy Best First vs BFS race side-by-side!")
    print("Yellow = Explored cells")
    print("Blue/Orange/Purple line = Path found")
    print("\nAlgorithm Differences:")
    print("  A*: f(n) = g(n) + h(n) - Guarantees shortest path")
    print("  Greedy: f(n) = h(n) only - Fast but NOT optimal")
    print("  BFS: FIFO queue - Guarantees shortest path (unweighted)")
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
    animator = ThreeWayPathfindingAnimator(start_grid, end_grid, speed=speed_input)
    animator.animate()
    
    print("\n[DONE] Animation window closed")
    print("=" * 60)

if __name__ == "__main__":
    main()

