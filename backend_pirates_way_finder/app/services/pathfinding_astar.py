"""
A* pathfinding implementation with proper Manhattan heuristic
GUARANTEES shortest path (just like Dijkstra, but faster!)
"""

import heapq
import math
from app.core.grid_loader import grid_instance
from app.core.database import nodes_collection

# Configuration: Buffer size around stair/ramp nodes (in grid cells)
# Adjust this to make the blocked/preferred areas larger or smaller
# Default: 2 cells (with 10px cell_size = 20px buffer in each direction)
ACCESSIBILITY_BUFFER_SIZE = 3 # Change this to adjust the size (1-5 recommended)

# Cache for ramp locations (loaded once)
_ramp_locations = None
# Cache for ramp cells (with buffer) - cells that ARE ramps
_ramp_cells = None
# Cache for stair blocked cells (loaded once)
_stair_blocked_cells = None

def get_ramp_locations():
    """Get all ramp node locations from MongoDB (cached)"""
    global _ramp_locations
    
    if _ramp_locations is None:
        _ramp_locations = []
        
        # Find all ramp nodes - check name, id, type, and accessible property
        ramp_nodes = nodes_collection.find({
            "$or": [
                {"properties.name": {"$regex": "ramp", "$options": "i"}},
                {"properties.id": {"$regex": "ramp", "$options": "i"}},
                {"properties.type": {"$in": ["ramp", "ramp_entry", "ramp_exit"]}},
                # Also check if accessible is explicitly True and not a stair
                {"properties.accessible": True, "properties.type": {"$ne": "stairs"}}
            ],
            "_meta.is_archived": {"$ne": True}
        })
        
        cell_size = grid_instance.cell_size
        for node in ramp_nodes:
            coords = node.get("geometry", {}).get("coordinates", [])
            if coords:
                px, py = coords[0], coords[1]
                gx, gy = px // cell_size, py // cell_size
                _ramp_locations.append((gx, gy))
                print(f"[RAMP] Detected at grid [{gx}, {gy}]")
        
        if not _ramp_locations:
            print("[WARN] No ramps found in database")
    
    return _ramp_locations

def get_ramp_cells():
    """
    Get all ramp locations from MongoDB and create a set of ramp grid cells.
    Includes a buffer around each ramp node to mark cells that ARE ramps.
    Returns a set of (x, y) grid coordinates that are ramp areas.
    """
    global _ramp_cells
    
    if _ramp_cells is None:
        _ramp_cells = set()
        
        # Find all ramp nodes - same query as get_ramp_locations
        # Check multiple criteria: name/id contains "ramp", type is ramp, OR accessible=True
        ramp_nodes = nodes_collection.find({
            "$or": [
                {"properties.name": {"$regex": "ramp", "$options": "i"}},
                {"properties.id": {"$regex": "ramp", "$options": "i"}},
                {"properties.type": {"$in": ["ramp", "ramp_entry", "ramp_exit"]}},
                # If accessible=True, it's likely a ramp (unless it's explicitly a stair)
                {"properties.accessible": True, "properties.type": {"$nin": ["stairs", "stairs_entry", "stairs_exit"]}}
            ],
            "_meta.is_archived": {"$ne": True}
        })
        
        cell_size = grid_instance.cell_size
        buffer_size = ACCESSIBILITY_BUFFER_SIZE
        
        ramp_count = 0
        for node in ramp_nodes:
            coords = node.get("geometry", {}).get("coordinates", [])
            if coords:
                px, py = coords[0], coords[1]
                gx, gy = px // cell_size, py // cell_size
                
                # Add buffer around ramp node (±buffer_size cells)
                for dx in range(-buffer_size, buffer_size + 1):
                    for dy in range(-buffer_size, buffer_size + 1):
                        nx = gx + dx
                        ny = gy + dy
                        # Only add if within grid bounds AND the cell is walkable
                        if 0 <= nx < grid_instance.w and 0 <= ny < grid_instance.h:
                            # Only mark as ramp if the cell is actually walkable (not a wall)
                            if grid_instance.grid[ny][nx] == 0:  # 0 = walkable
                                _ramp_cells.add((nx, ny))
                
                ramp_count += 1
                print(f"[RAMP] Marked area around grid [{gx}, {gy}] as ramp (buffer: ±{buffer_size} cells)")
        
        if ramp_count == 0:
            print("[WARN] No ramp cells marked")
        else:
            print(f"[ACCESSIBILITY] Marked {len(_ramp_cells)} cells as ramp areas around {ramp_count} ramp location(s)")
    
    return _ramp_cells

def get_stair_blocked_cells():
    """
    Get all stair locations from MongoDB and create a set of blocked grid cells.
    Includes a buffer around each stair node to ensure paths don't go through stairs.
    Returns a set of (x, y) grid coordinates that should be blocked in accessibility mode.
    """
    global _stair_blocked_cells
    
    if _stair_blocked_cells is None:
        _stair_blocked_cells = set()
        
        # Find all stair nodes - check multiple criteria
        # Match: type="stairs", type="stairs_entry", type="stairs_exit"
        # OR name/id contains "stair" or "step"
        # OR accessible=False AND type is not "ramp"
        stair_nodes = nodes_collection.find({
            "$or": [
                {"properties.name": {"$regex": "stair|step", "$options": "i"}},
                {"properties.id": {"$regex": "stair|step", "$options": "i"}},
                {"properties.type": {"$in": ["stairs", "stairs_entry", "stairs_exit", "stair"]}},
                # Also check if accessible is explicitly False (and not a ramp)
                {"properties.accessible": False, "properties.type": {"$ne": "ramp"}},
                # Explicit check for type="stairs" with accessible=False
                {"properties.type": "stairs", "properties.accessible": False}
            ],
            "_meta.is_archived": {"$ne": True}
        })
        
        cell_size = grid_instance.cell_size
        buffer_size = ACCESSIBILITY_BUFFER_SIZE
        
        stair_count = 0
        for node in stair_nodes:
            coords = node.get("geometry", {}).get("coordinates", [])
            if coords:
                px, py = coords[0], coords[1]
                gx, gy = px // cell_size, py // cell_size
                
                # Skip if it's actually a ramp (double-check by name, id, type, and accessible)
                props = node.get("properties", {})
                node_name = props.get("name", "").lower()
                node_id = props.get("id", "").lower()
                node_type = str(props.get("type", "")).lower()
                is_accessible = props.get("accessible", None)
                
                # If it's marked as accessible=True, it's probably a ramp, not stairs
                if is_accessible is True:
                    print(f"[STAIRS] Skipping {node_name or node_id} - marked as accessible=True (likely a ramp)")
                    continue
                # If name/id/type contains "ramp", skip it
                if "ramp" in node_name or "ramp" in node_id or "ramp" in node_type:
                    print(f"[STAIRS] Skipping {node_name or node_id} - contains 'ramp' in name/id/type")
                    continue
                
                # Add buffer around stair node (±buffer_size cells)
                cells_blocked = 0
                for dx in range(-buffer_size, buffer_size + 1):
                    for dy in range(-buffer_size, buffer_size + 1):
                        nx = gx + dx
                        ny = gy + dy
                        # Only add if within grid bounds AND the cell is walkable (not a wall)
                        if 0 <= nx < grid_instance.w and 0 <= ny < grid_instance.h:
                            # Only block walkable cells (not walls)
                            if grid_instance.grid[ny][nx] == 0:  # 0 = walkable
                                _stair_blocked_cells.add((nx, ny))
                                cells_blocked += 1
                
                stair_count += 1
                print(f"[STAIRS] ✅ Blocked {cells_blocked} cells around '{node_name or node_id}' at grid [{gx}, {gy}] (buffer: ±{buffer_size} cells)")
        
        if stair_count == 0:
            print("[WARN] ⚠️ No stair nodes found in database")
            print("[WARN]    Check that your nodes have:")
            print("[WARN]    - type: 'stairs' OR name/id contains 'stair' OR accessible: false")
        else:
            print(f"[ACCESSIBILITY] ✅ Blocked {len(_stair_blocked_cells)} cells around {stair_count} stair location(s)")
    
    return _stair_blocked_cells

def distance_to_nearest_ramp(x, y, ramp_locations):
    """Calculate Manhattan distance to nearest ramp"""
    if not ramp_locations:
        return 0
    
    min_dist = float('inf')
    for rx, ry in ramp_locations:
        dist = abs(x - rx) + abs(y - ry)
        min_dist = min(min_dist, dist)
    
    return min_dist

def count_adjacent_walls(x, y):
    """Count how many walls are adjacent to this cell (for aesthetic spacing)"""
    g = grid_instance.grid
    wall_count = 0
    
    # Check all 8 surrounding cells (including diagonals)
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            
            nx, ny = x + dx, y + dy
            if 0 <= nx < grid_instance.w and 0 <= ny < grid_instance.h:
                if g[ny][nx] == 1:  # Wall
                    wall_count += 1
    
    return wall_count

def get_neighbors(x, y, accessibility_mode=False, stair_blocked_cells=None):
    """
    Get walkable neighboring cells.
    In accessibility mode, also blocks stair cells.
    """
    dirs = [(1,0), (-1,0), (0,1), (0,-1)]
    g = grid_instance.grid
    
    # Get stair blocked cells if in accessibility mode
    if accessibility_mode and stair_blocked_cells is None:
        stair_blocked_cells = get_stair_blocked_cells()
    
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
    """
    Manhattan distance heuristic
    
    This is an "admissible" heuristic, meaning it NEVER overestimates
    the actual distance. This guarantees A* finds the shortest path!
    
    Why Manhattan? Because we can only move up/down/left/right (no diagonals)
    """
    return abs(x - goal_x) + abs(y - goal_y)

def astar(start_px, start_py, end_px, end_py, accessibility_mode=False):
    """
    A* pathfinding with Manhattan heuristic
    
    GUARANTEES shortest path (just like Dijkstra)
    But FASTER because it explores toward the goal
    
    f(n) = g(n) + h(n)
    where:
      g(n) = actual cost from start to n
      h(n) = estimated cost from n to goal (Manhattan distance)
      f(n) = total estimated cost through n
    """
    cell = grid_instance.cell_size
    
    # Convert pixel → grid coords
    sx = start_px // cell
    sy = start_py // cell
    ex = end_px // cell
    ey = end_py // cell
    
    start = (sx, sy)
    end = (ex, ey)
    
    # Get ramp cells and stair blocked cells if accessibility mode is ON
    ramp_cells = None
    stair_blocked_cells = None
    if accessibility_mode:
        ramp_cells = get_ramp_cells()
        stair_blocked_cells = get_stair_blocked_cells()
        if ramp_cells:
            print(f"[ACCESSIBILITY] Marked {len(ramp_cells)} cells as ramps - paths will PREFER them")
        else:
            print("[ACCESSIBILITY] No ramps found")
        if stair_blocked_cells:
            print(f"[ACCESSIBILITY] Blocking {len(stair_blocked_cells)} stair cells - paths will AVOID them")
        else:
            print("[ACCESSIBILITY] No stairs found to block")
        
        # Warn if start or end is in a blocked stair area
        if stair_blocked_cells:
            if start in stair_blocked_cells:
                print(f"[WARN] Start point {start} is in a stair area - pathfinding may be limited")
            if end in stair_blocked_cells:
                print(f"[WARN] End point {end} is in a stair area - pathfinding may be limited")
    
    # Priority queue: (f_cost, g_cost, node)
    # f = g + h (total estimated cost)
    # g = actual cost from start
    h_start = manhattan_heuristic(sx, sy, ex, ey)
    pq = [(h_start, 0, start)]
    
    dist = {start: 0}  # g-costs
    prev = {}
    visited = set()
    
    while pq:
        f_cost, g_cost, (x, y) = heapq.heappop(pq)
        
        if (x, y) in visited:
            continue
        visited.add((x, y))
        
        if (x, y) == end:
            break
        
        for nx, ny in get_neighbors(x, y, accessibility_mode, stair_blocked_cells):
            # Base cost is 1 for moving to a neighbor
            base_cost = 1
            
            # AESTHETIC: Add penalty for cells near walls (keeps path centered in corridors)
            adjacent_walls = count_adjacent_walls(nx, ny)
            if adjacent_walls > 0:
                # Penalty for being near walls (0.3 per adjacent wall)
                # Higher penalty = more spacing from walls
                wall_penalty = adjacent_walls * 0.3
                base_cost += wall_penalty
            
            # In accessibility mode, make ramps cheaper (so paths prefer going through them)
            if accessibility_mode and ramp_cells:
                if (nx, ny) in ramp_cells:
                    # This cell IS a ramp - make it cheaper (0.6 cost instead of 1)
                    # This encourages paths to use ramps without forcing them
                    base_cost = 0.6  # Cheaper than regular cells, but not too cheap
            
            new_g = g_cost + base_cost
            
            if (nx, ny) not in dist or new_g < dist[(nx, ny)]:
                dist[(nx, ny)] = new_g
                prev[(nx, ny)] = (x, y)
                
                # Calculate f = g + h
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
    
    # Check if path was found
    if len(path) == 1 and path[0] == start:
        # No path found - end is unreachable
        print(f"[WARN] No path found from {start} to {end}")
        if accessibility_mode:
            print("[WARN] This might be because stairs are blocking all routes, or no accessible path exists")
        return []
    
    # Convert back to pixel coordinates
    pixel_path = [
        {
            "x": x * cell + cell/2,
            "y": y * cell + cell/2
        }
        for x, y in path
    ]
    
    print(f"[PATHFINDING] Found path with {len(pixel_path)} waypoints")
    if accessibility_mode:
        # Count how many ramp cells are in the path
        if ramp_cells:
            ramp_cells_in_path = sum(1 for x, y in path if (x, y) in ramp_cells)
            print(f"[ACCESSIBILITY] Path uses {ramp_cells_in_path} ramp cells")
    
    return pixel_path


def simplify_path(path_coordinates, tolerance=20):
    """
    Simplify path using Douglas-Peucker-like algorithm to reduce points
    while maintaining path shape.
    """
    if len(path_coordinates) <= 2:
        return path_coordinates
    
    simplified = [path_coordinates[0]]
    
    for i in range(1, len(path_coordinates) - 1):
        prev = path_coordinates[i - 1]
        curr = path_coordinates[i]
        next_point = path_coordinates[i + 1]
        
        # Calculate vectors
        v1 = (curr['x'] - prev['x'], curr['y'] - prev['y'])
        v2 = (next_point['x'] - curr['x'], next_point['y'] - curr['y'])
        
        # Normalize
        v1_len = math.sqrt(v1[0]**2 + v1[1]**2)
        v2_len = math.sqrt(v2[0]**2 + v2[1]**2)
        
        if v1_len > 0 and v2_len > 0:
            v1 = (v1[0]/v1_len, v1[1]/v1_len)
            v2 = (v2[0]/v2_len, v2[1]/v2_len)
            
            # Calculate angle
            dot = v1[0]*v2[0] + v1[1]*v2[1]
            dot = max(-1.0, min(1.0, dot))
            angle_deg = math.degrees(math.acos(dot))
            
            # Keep point if angle is significant (>3 degrees)
            if angle_deg > 3:
                simplified.append(curr)
    
    simplified.append(path_coordinates[-1])
    return simplified


def smooth_path(path_coordinates, smoothing_factor=0.3):
    """
    Smooth path using Catmull-Rom spline interpolation.
    Creates smooth curves between path points for better visual appearance.
    
    Args:
        path_coordinates: List of {x, y} coordinate dictionaries
        smoothing_factor: Controls smoothness (0.0 = no smoothing, 1.0 = maximum smoothing)
    
    Returns:
        Smoothed path with interpolated points
    """
    if not path_coordinates or len(path_coordinates) < 3:
        return path_coordinates
    
    smoothed = [path_coordinates[0]]  # Start point
    
    for i in range(len(path_coordinates) - 1):
        p0 = path_coordinates[max(0, i - 1)]
        p1 = path_coordinates[i]
        p2 = path_coordinates[i + 1]
        p3 = path_coordinates[min(len(path_coordinates) - 1, i + 2)]
        
        # Number of interpolated points between each pair
        num_points = max(2, int(10 * smoothing_factor))
        
        for j in range(1, num_points):
            t = j / num_points
            
            # Catmull-Rom spline interpolation
            t2 = t * t
            t3 = t2 * t
            
            # Basis functions
            b0 = -0.5 * t3 + t2 - 0.5 * t
            b1 = 1.5 * t3 - 2.5 * t2 + 1.0
            b2 = -1.5 * t3 + 2.0 * t2 + 0.5 * t
            b3 = 0.5 * t3 - 0.5 * t2
            
            # Interpolated point
            x = b0 * p0['x'] + b1 * p1['x'] + b2 * p2['x'] + b3 * p3['x']
            y = b0 * p0['y'] + b1 * p1['y'] + b2 * p2['y'] + b3 * p3['y']
            
            smoothed.append({'x': x, 'y': y})
        
        # Add the next control point
        if i < len(path_coordinates) - 2:
            smoothed.append(p2)
    
    # Always include the end point
    if smoothed[-1] != path_coordinates[-1]:
        smoothed.append(path_coordinates[-1])
    
    return smoothed


def generate_instructions_from_grid_path(path_coordinates, pixel_to_meter=0.02, angle_threshold=2):
    """
    Generate turn-by-turn instructions from a grid-based path.
    More sensitive to direction changes.
    """
    if not path_coordinates or len(path_coordinates) < 2:
        return ["You are already at your destination."]
    
    if len(path_coordinates) == 2:
        dx = path_coordinates[1]['x'] - path_coordinates[0]['x']
        dy = path_coordinates[1]['y'] - path_coordinates[0]['y']
        distance_m = math.sqrt(dx ** 2 + dy ** 2) * pixel_to_meter
        return [f"Walk straight for {round(distance_m, 1)} meters to your destination"]
    
    instructions = []
    accumulated_distance = 0
    current_direction = None
    
    # History of recent turn directions for pattern detection
    recent_turns = []
    CONSECUTIVE_TURN_COUNT = 2  # Number of consecutive turns to detect a pattern
    MAJORITY_CHECK_WINDOW = 3
    MIN_DISTANCE_METERS = 0.1  # Minimum distance before creating instruction
    MIN_DISTANCE_METERS_FINAL = 0.1
    
    for i in range(len(path_coordinates) - 1):
        current = path_coordinates[i]
        next_point = path_coordinates[i + 1]
        
        dx = next_point['x'] - current['x']
        dy = next_point['y'] - current['y']
        distance_px = math.sqrt(dx ** 2 + dy ** 2)
        distance_m = distance_px * pixel_to_meter
        
        if i == 0:
            accumulated_distance = distance_m
            current_direction = 'straight'
            continue
        
        prev_point = path_coordinates[i - 1]
        v1 = (current['x'] - prev_point['x'], current['y'] - prev_point['y'])
        v2 = (next_point['x'] - current['x'], next_point['y'] - current['y'])
        
        v1_len = math.sqrt(v1[0]**2 + v1[1]**2)
        v2_len = math.sqrt(v2[0]**2 + v2[1]**2)
        if v1_len > 0 and v2_len > 0:
            v1 = (v1[0]/v1_len, v1[1]/v1_len)
            v2 = (v2[0]/v2_len, v2[1]/v2_len)
            
            dot = v1[0]*v2[0] + v1[1]*v2[1]
            dot = max(-1.0, min(1.0, dot))
            angle_rad = math.acos(dot)
            angle_deg = math.degrees(angle_rad)
            
            cross = v1[0]*v2[1] - v1[1]*v2[0]
            
            segment_direction = 'straight'
            if angle_deg > angle_threshold:
                if cross > 0:
                    segment_direction = 'left'
                else:
                    segment_direction = 'right'
            
            # Update recent turns history
            recent_turns.append(segment_direction)
            if len(recent_turns) > MAJORITY_CHECK_WINDOW:
                recent_turns.pop(0)
            
            # Check for consistent turn pattern
            turn_pattern_detected = False
            if segment_direction != 'straight':
                consecutive_count = 0
                for j in range(len(recent_turns) - 1, -1, -1):
                    if recent_turns[j] == segment_direction:
                        consecutive_count += 1
                    else:
                        break
                if consecutive_count >= CONSECUTIVE_TURN_COUNT:
                    turn_pattern_detected = True
            
            # Determine if a new instruction is needed
            should_create_instruction = False
            if segment_direction != current_direction and accumulated_distance * pixel_to_meter >= MIN_DISTANCE_METERS:
                should_create_instruction = True
            elif turn_pattern_detected and current_direction == 'straight' and accumulated_distance * pixel_to_meter >= MIN_DISTANCE_METERS:
                should_create_instruction = True
            
            if should_create_instruction:
                if current_direction == 'straight':
                    instructions.append(f"Walk straight for {round(accumulated_distance, 1)} meters")
                elif current_direction == 'left':
                    instructions.append(f"Turn left and continue for {round(accumulated_distance, 1)} meters")
                elif current_direction == 'right':
                    instructions.append(f"Turn right and continue for {round(accumulated_distance, 1)} meters")
                
                accumulated_distance = 0
                current_direction = segment_direction
        
        accumulated_distance += distance_m
    
    if accumulated_distance * pixel_to_meter >= MIN_DISTANCE_METERS_FINAL:
        if current_direction == 'straight':
            instructions.append(f"Continue straight for {round(accumulated_distance, 1)} meters to your destination")
        elif current_direction == 'left':
            instructions.append(f"Turn left for {round(accumulated_distance, 1)} meters to your destination")
        elif current_direction == 'right':
            instructions.append(f"Turn right for {round(accumulated_distance, 1)} meters to your destination")
    
    if not instructions:
        total_dist = sum(
            math.sqrt((path_coordinates[i+1]['x'] - path_coordinates[i]['x'])**2 + 
                     (path_coordinates[i+1]['y'] - path_coordinates[i]['y'])**2) * pixel_to_meter
            for i in range(len(path_coordinates) - 1)
        )
        instructions.append(f"Walk straight for {round(total_dist, 1)} meters to your destination")
    
    return instructions

