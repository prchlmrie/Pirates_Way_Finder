from typing import List, Dict
from app.core.database import nodes_collection # 🎯 Use MongoDB for efficient querying
from fastapi import HTTPException # For potential error handling

# 🎯 NOTE: We import the correct service function to avoid duplicating query logic
from .node_service import get_all_pois 

def get_all_locations_in_building(building_id: str) -> List[Dict]:
    """
    Fetch all active Node/POI locations inside a specific building by querying MongoDB.
    
    This replaces the slow nested Firestore logic with a single indexed MongoDB query.
    """
    if not building_id:
        raise HTTPException(status_code=400, detail="Building ID is required.")
        
    # 🎯 Delegate the work to the primary Node/POI retrieval function for consistency
    locations = get_all_pois(building_id=building_id)
    
    if not locations:
        raise HTTPException(status_code=404, detail=f"No locations found for building ID: {building_id}")

    return locations