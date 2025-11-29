from fastapi import APIRouter
from app.services.building_service import get_all_locations_in_building
from app.services.node_service import get_locations_by_category # 🎯 New import for the moved function

router = APIRouter(prefix="/buildings", tags=["Building Data"]) # 🎯 Added prefix for cleaner URLs

# 1. Fetch all locations in a building (Original route)
@router.get("/{building_id}/locations", summary="Get all locations within a specific building")
def fetch_all_building_locations(building_id: str):
    """Retrieves a list of all locations (Nodes/POIs) associated with the given building ID."""
    locations = get_all_locations_in_building(building_id)
    return {
        "building": building_id,
        "count": len(locations),
        "locations": locations
    }

# 2. Fetch locations filtered by category (Moved from location_router.py)
@router.get("/{building_id}/categories/{category_id}/locations", summary="Get locations in a building filtered by category")
def fetch_locations_by_category(building_id: str, category_id: str):
    """Retrieves locations within a building that match the specified category."""
    locations = get_locations_by_category(building_id, category_id)
    return {
        "building": building_id,
        "category": category_id,
        "count": len(locations),
        "locations": locations
    }