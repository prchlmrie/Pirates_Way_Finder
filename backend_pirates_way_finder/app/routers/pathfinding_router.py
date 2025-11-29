from fastapi import APIRouter, Query
from app.services.pathfinding_service import find_shortest_path

router = APIRouter(prefix="/navigate", tags=["Navigation"])

@router.get("/")
def navigate(
    from_id: str = Query(...),
    to_id: str = Query(...),
    accessible_only: bool = Query(False)
):
    """
    Example: /navigate?from_id=lecafe&to_id=stair_sotero_1a&accessible_only=true
    """
    result = find_shortest_path(from_id, to_id, accessible_only)
    return result