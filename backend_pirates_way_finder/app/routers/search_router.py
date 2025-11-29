from fastapi import APIRouter, Query
# 🎯 Import the existing service function
from app.services.search_service import search_locations
from typing import Optional, List, Dict

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/", summary="Search locations by query and optional filters")
def search_locations_route(
    query: str = Query(..., description="The main search keyword (required)"), # Changed to required string
    category: Optional[str] = Query(None, description="Filter results by category (e.g., office, amenity)"),
    building_id: Optional[str] = Query(None, description="Filter results by building ID")
):
    """
    Retrieves locations matching the provided query, potentially filtered by category and building.
    """
    # 🎯 Delegate logic. The service should handle the filtering if possible.
    results_data = search_locations(
        query=query, 
        category=category, 
        building_id=building_id
    )

    return {
        "query": query,
        "category": category,
        "building_id": building_id,
        "count": results_data.get("count", 0),
        "results": results_data.get("results", [])
    }