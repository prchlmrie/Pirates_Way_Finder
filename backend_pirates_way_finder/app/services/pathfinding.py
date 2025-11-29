import heapq
from app.core.grid_loader import grid_instance
from app.core.database import nodes_collection

# Cache for ramp locations (loaded once)
_ramp_locations = None

def get_ramp_locations():
    """Get all ramp node locations from MongoDB (cached)"""
    global _ramp_locations
    
    if _ramp_locations is None:
        _ramp_locations = []
        
        # Find all ramp nodes
        ramp_nodes = nodes_collection.find({
            "$or": [
                {"properties.name": {"$regex": "ramp", "$options": "i"}},
                {"properties.id": {"$regex": "ramp", "$options": "i"}},
                {"properties.type": "ramp"}
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

def dijkstra(start_px, start_py, end_px, end_py, accessibility_mode=False):
    cell = grid_instance.cell_size

    # Convert pixel → grid coords
    sx = start_px // cell
    sy = start_py // cell
    ex = end_px // cell
    ey = end_py // cell

    start = (sx, sy)
    end = (ex, ey)

    # Get ramp locations if accessibility mode is ON
    ramp_locations = []
    if accessibility_mode:
        ramp_locations = get_ramp_locations()
        if ramp_locations:
            print(f"[ACCESSIBILITY] Using {len(ramp_locations)} ramp location(s)")
        else:
            print("[ACCESSIBILITY] No ramps found, using standard routing")

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
            # Base cost is 1 for moving to a neighbor
            base_cost = 1
            
            # AESTHETIC: Add penalty for cells near walls (keeps path centered in corridors)
            adjacent_walls = count_adjacent_walls(nx, ny)
            if adjacent_walls > 0:
                # Penalty for being near walls (0.3 per adjacent wall)
                # Higher penalty = more spacing from walls
                wall_penalty = adjacent_walls * 0.3
                base_cost += wall_penalty
            
            # In accessibility mode, add penalty for being far from ramps
            if accessibility_mode and ramp_locations:
                dist_to_ramp = distance_to_nearest_ramp(nx, ny, ramp_locations)
                
                # Add penalty based on distance from ramp
                # Cells near ramps (within 20 cells) have lower cost
                # Cells far from ramps have higher cost
                if dist_to_ramp > 20:
                    penalty = (dist_to_ramp - 20) * 0.5  # Penalty increases with distance
                    base_cost += penalty
            
            new_cost = cost + base_cost
            if (nx, ny) not in dist or new_cost < dist[(nx, ny)]:
                dist[(nx, ny)] = new_cost
                prev[(nx, ny)] = (x, y)
                heapq.heappush(pq, (new_cost, (nx, ny)))

    # reconstruct path
    path = []
    cur = end
    while cur in prev:
        path.append(cur)
        cur = prev[cur]
    path.append(start)
    path.reverse()

    # convert back to pixel coordinates
    pixel_path = [
        {
            "x": x * cell + cell/2,
            "y": y * cell + cell/2
        }
        for x, y in path
    ]

    return pixel_path