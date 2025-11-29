from fastapi import APIRouter
from pydantic import BaseModel
from app.services.pathfinding_astar import astar, simplify_path, smooth_path, generate_instructions_from_grid_path
from app.core.grid_loader import grid_instance
import math

router = APIRouter(prefix="/path", tags=["Pathfinding"])

class PathRequest(BaseModel):
    start_x: int
    start_y: int
    end_x: int
    end_y: int
    accessibility_mode: bool = False

@router.post("/shortest")
def shortest_path(req: PathRequest):
    # Using A* algorithm (2-4x faster than Dijkstra, same shortest path!)
    path = astar(req.start_x, req.start_y, req.end_x, req.end_y, req.accessibility_mode)
    
    if not path or len(path) == 0:
        return {
            "path": [],
            "instructions": [],
            "distance_meters": 0,
            "estimated_time_minutes": 0
        }
    
    # Apply path smoothing for visual appeal (Catmull-Rom spline)
    smoothed_path = smooth_path(path, smoothing_factor=0.3) if path and len(path) > 2 else path
    
    # Calculate total distance using original path (not smoothed) for accuracy
    total_distance = 0
    if len(path) > 1:
        for i in range(len(path) - 1):
            dx = path[i + 1]['x'] - path[i]['x']
            dy = path[i + 1]['y'] - path[i]['y']
            segment_distance = (dx ** 2 + dy ** 2) ** 0.5
            total_distance += segment_distance
    
    PIXEL_TO_METER = 0.02
    distance_meters = total_distance * PIXEL_TO_METER
    AVERAGE_WALK_SPEED = 1.4  # m/s
    estimated_time_seconds = distance_meters / AVERAGE_WALK_SPEED
    
    # Generate instructions using simplified path (not smoothed, for accuracy)
    instructions = []
    if path and len(path) > 0:
        simplified_path = simplify_path(path, tolerance=20)
        print(f"[INSTRUCTIONS] Simplified path from {len(path)} to {len(simplified_path)} points")
        instructions = generate_instructions_from_grid_path(simplified_path, PIXEL_TO_METER, angle_threshold=2)
        print(f"[INSTRUCTIONS] ✅ Generated {len(instructions)} instructions")
    
    return {
        "path": smoothed_path,  # Return smoothed path for rendering
        "instructions": instructions,
        "distance_meters": round(distance_meters, 2),
        "estimated_time_minutes": round(estimated_time_seconds / 60, 2)
    }

@router.get("/walkable-grid")
def get_walkable_grid():
    """
    Returns all walkable cells from the grid for visualization
    """
    walkable_cells = []
    cell_size = grid_instance.cell_size
    
    for y in range(grid_instance.h):
        for x in range(grid_instance.w):
            if grid_instance.grid[y][x] == 0:  # Walkable cell
                # Convert grid coordinates to pixel coordinates (center of cell)
                px = x * cell_size + cell_size / 2
                py = y * cell_size + cell_size / 2
                walkable_cells.append({"x": px, "y": py})
    
    return {
        "walkable_cells": walkable_cells,
        "cell_size": cell_size,
        "grid_width": grid_instance.w,
        "grid_height": grid_instance.h
    }