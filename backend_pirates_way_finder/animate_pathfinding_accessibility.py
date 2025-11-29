"""
Interactive side-by-side pathfinding animation with ACCESSIBILITY MODE
Watch Dijkstra vs A* race using only ramps (avoiding stairs)!
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import heapq
import time
from app.core.grid_loader import grid_instance
from app.services.pathfinding_astar import get_stair_blocked_cells, get_ramp_cells
from PIL import Image
import numpy as np

# Load grid first
print("[LOADING] Grid data...")
grid_instance.load("app/static/grid.json")
print(f"[OK] Grid loaded: {grid_instance.w}x{grid_instance.h} cells")

# Load accessibility data
print("[LOADING] Accessibility data (stairs and ramps)...")
stair_blocked_cells = get_stair_blocked_cells()
ramp_cells = get_ramp_cells()
print(f"[OK] Loaded {len(stair_blocked_cells)} stair cells and {len(ramp_cells)} ramp cells")

def get_neighbors(x, y, accessibility_mode=True, stair_blocked_cells=None):
    """Get walkable neighboring cells with accessibility support"""
    dirs = [(1,0), (-1,0), (0,1), (0,-1)]
    g = grid_instance.grid
    
    for dx, dy in dirs:
        nx = x + dx
        ny = y + dy
        if 0 <= nx < grid_instance.w and 0 <= ny < grid_instance.h:
            # Check if cell is walkable (not a wall)
            if g[ny][nx] == 0:  # walkable
                # In accessibility mode, also check if it's a blocked stair cell
                if accessibility_mode and stair_blocked_cells:
                    if (nx, ny) in stair_blocked_cells:
                        continue  # Skip this cell - it's a stair area
                yield nx, ny

def manhattan_heuristic(x, y, goal_x, goal_y):
    """Manhattan distance heuristic"""
    return abs(x - goal_x) + abs(y - goal_y)

class AccessibilityPathfindingAnimator:
    def __init__(self, start, end, speed='fast'):
        self.start = start
        self.end = end
        self.cell_size = grid_instance.cell_size
        self.stair_blocked_cells = stair_blocked_cells
        self.ramp_cells = ramp_cells
        
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
        
        print(f"[READY] Accessibility animation initialized")
        print(f"[INFO] Update interval: {self.update_interval} steps per frame")
        print(f"[INFO] Using {len(self.ramp_cells)} ramp cells (preferred)")
        print(f"[INFO] Blocking {len(self.stair_blocked_cells)} stair cells")
    
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
        """Execute one step of Dijkstra with accessibility"""
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
        
        # Use accessibility-aware neighbors
        for nx, ny in get_neighbors(x, y, accessibility_mode=True, stair_blocked_cells=self.stair_blocked_cells):
            # Base cost is 1, but make ramps cheaper
            base_cost = 1
            if (nx, ny) in self.ramp_cells:
                base_cost = 0.6  # Prefer ramps
            
            new_cost = cost + base_cost
            if (nx, ny) not in state['dist'] or new_cost < state['dist'][(nx, ny)]:
                state['dist'][(nx, ny)] = new_cost
                state['prev'][(nx, ny)] = (x, y)
                heapq.heappush(state['pq'], (new_cost, (nx, ny)))
        
        return True
    
    def step_astar(self):
        """Execute one step of A* with accessibility"""
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
        # Use accessibility-aware neighbors
        for nx, ny in get_neighbors(x, y, accessibility_mode=True, stair_blocked_cells=self.stair_blocked_cells):
            # Base cost is 1, but make ramps cheaper
            base_cost = 1
            if (nx, ny) in self.ramp_cells:
                base_cost = 0.6  # Prefer ramps
            
            new_g = g_cost + base_cost
            
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
        fig.suptitle('Accessibility Mode: Dijkstra vs A* (Using Ramps Only)', fontsize=16, fontweight='bold')
        
        # Setup both axes
        for ax in [ax1, ax2]:
            ax.imshow(map_array, extent=[0, map_img.width, map_img.height, 0], alpha=0.3)
            ax.set_xlim(0, map_img.width)
            ax.set_ylim(map_img.height, 0)
            ax.axis('off')
        
        ax1.set_title('Dijkstra (Accessibility)', fontsize=14, fontweight='bold', color='blue')
        ax2.set_title('A* (Accessibility)', fontsize=14, fontweight='bold', color='red')
        
        # Draw stair cells (orange) and ramp cells (blue) as background
        for ax in [ax1, ax2]:
            # Draw stair cells
            for sx, sy in list(self.stair_blocked_cells)[::10]:  # Sample every 10th for performance
                px = sx * self.cell_size + self.cell_size/2
                py = sy * self.cell_size + self.cell_size/2
                rect = patches.Rectangle(
                    (px - self.cell_size/2, py - self.cell_size/2),
                    self.cell_size, self.cell_size,
                    linewidth=0, facecolor='orange', alpha=0.2, zorder=1
                )
                ax.add_patch(rect)
            
            # Draw ramp cells
            for rx, ry in list(self.ramp_cells)[::10]:  # Sample every 10th for performance
                px = rx * self.cell_size + self.cell_size/2
                py = ry * self.cell_size + self.cell_size/2
                rect = patches.Rectangle(
                    (px - self.cell_size/2, py - self.cell_size/2),
                    self.cell_size, self.cell_size,
                    linewidth=0, facecolor='cyan', alpha=0.15, zorder=1
                )
                ax.add_patch(rect)
        
        # Initialize scatter plots for visited cells
        dijkstra_scatter = ax1.scatter([], [], c='yellow', s=10, alpha=0.3, marker='s', zorder=5)
        astar_scatter = ax2.scatter([], [], c='yellow', s=10, alpha=0.3, marker='s', zorder=5)
        
        # Initialize path lines
        dijkstra_path_line, = ax1.plot([], [], 'b-', linewidth=3, label='Path', zorder=10)
        astar_path_line, = ax2.plot([], [], 'r-', linewidth=3, label='Path', zorder=10)
        
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
        
        # Legend
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], color='orange', lw=4, alpha=0.3, label='Stairs (Blocked)'),
            Line2D([0], [0], color='cyan', lw=4, alpha=0.3, label='Ramps (Preferred)'),
            Line2D([0], [0], color='yellow', lw=4, alpha=0.3, label='Explored'),
        ]
        ax1.legend(handles=legend_elements, loc='lower right', fontsize=9)
        ax2.legend(handles=legend_elements, loc='lower right', fontsize=9)
        
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
            
            # Count ramp cells in path
            dijkstra_path = self.get_path(self.dijkstra_state)
            ramp_count_dijkstra = sum(1 for x, y in dijkstra_path if (x, y) in self.ramp_cells) if dijkstra_path else 0
            
            astar_path = self.get_path(self.astar_state)
            ramp_count_astar = sum(1 for x, y in astar_path if (x, y) in self.ramp_cells) if astar_path else 0
            
            # Update stats
            dijkstra_text = f"Dijkstra (Accessibility)\n"
            dijkstra_text += f"Steps: {self.dijkstra_state['steps']:,}\n"
            dijkstra_text += f"Explored: {len(self.dijkstra_state['visited']):,}\n"
            if self.dijkstra_done:
                dijkstra_text += f"Path: {len(dijkstra_path)} cells\n"
                dijkstra_text += f"Ramps used: {ramp_count_dijkstra}\n"
                dijkstra_text += f"✓ FOUND!"
            else:
                dijkstra_text += f"Status: Searching..."
            stats_dijkstra.set_text(dijkstra_text)
            
            astar_text = f"A* (Accessibility)\n"
            astar_text += f"Steps: {self.astar_state['steps']:,}\n"
            astar_text += f"Explored: {len(self.astar_state['visited']):,}\n"
            if self.astar_done:
                astar_text += f"Path: {len(astar_path)} cells\n"
                astar_text += f"Ramps used: {ramp_count_astar}\n"
                astar_text += f"✓ FOUND!"
            else:
                astar_text += f"Status: Searching..."
            stats_astar.set_text(astar_text)
            
            # Stop animation when both are done
            if self.dijkstra_done and self.astar_done:
                print(f"\n[COMPLETE] Both algorithms finished!")
                print(f"[DIJKSTRA] Explored {len(self.dijkstra_state['visited']):,} cells, Path: {len(dijkstra_path)}, Ramps: {ramp_count_dijkstra}")
                print(f"[A*] Explored {len(self.astar_state['visited']):,} cells, Path: {len(astar_path)}, Ramps: {ramp_count_astar}")
                
                if len(dijkstra_path) == len(astar_path):
                    print(f"[SUCCESS] Both found SAME accessible path!")
                else:
                    print(f"[INFO] Different path lengths (both are valid accessible paths)")
                
                # Keep showing for a bit
                if frame > self.frame + 10:
                    plt.close()
            
            return dijkstra_scatter, astar_scatter, dijkstra_path_line, astar_path_line, stats_dijkstra, stats_astar
        
        # Create animation
        print(f"\n[STARTING] Accessibility animation...")
        print(f"[TIP] Close the window when you're done watching!")
        print(f"[LEGEND] Orange = Stairs (blocked), Cyan = Ramps (preferred)")
        anim = FuncAnimation(fig, update, frames=range(10000), 
                           interval=50, blit=True, repeat=False)
        
        plt.tight_layout()
        plt.show()
        
        return anim

def main():
    print("=" * 60)
    print("ACCESSIBILITY MODE PATHFINDING RACE ANIMATION")
    print("=" * 60)
    print("\nWatch Dijkstra vs A* race using ONLY RAMPS (avoiding stairs)!")
    print("🟠 Orange = Stair cells (BLOCKED)")
    print("🔵 Cyan = Ramp cells (PREFERRED)")
    print("🟡 Yellow = Explored cells")
    print("🔵/🔴 Line = Accessible path")
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
    print(f"  Mode:  ACCESSIBILITY (ramps only, no stairs)")
    
    # Check if start/end are in blocked areas
    if start_grid in stair_blocked_cells:
        print(f"  ⚠️  WARN: Start is in a stair area!")
    if end_grid in stair_blocked_cells:
        print(f"  ⚠️  WARN: End is in a stair area!")
    
    # Create and run animation
    animator = AccessibilityPathfindingAnimator(start_grid, end_grid, speed=speed_input)
    animator.animate()
    
    print("\n[DONE] Animation window closed")
    print("=" * 60)

if __name__ == "__main__":
    main()

