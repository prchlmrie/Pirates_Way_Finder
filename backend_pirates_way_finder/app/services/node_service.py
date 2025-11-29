from typing import Dict, List, Optional
# 🎯 NOTE: You'll still need to import NodeFeature/NodeDB in any service using them for type hints!
# from app.models.node_model import NodeFeature 
from app.core.database import nodes_collection
from pymongo.errors import DuplicateKeyError
import re
from datetime import datetime
from fastapi import HTTPException

# --- Utility Function ---
def sanitize_id(raw_id: str) -> str:
    return re.sub(r"\s+", "_", raw_id.strip().lower())

# --- Retrieval Functions ---
# 🎯 Updated return type hint from List[Location] to List[Dict]
def get_locations_by_category(building_id: str, category_id: str) -> List[Dict]:
    """
    Fetch all ACTIVE POIs under a specific category in a specific building.
    """
    query = {
        "properties.building": building_id,
        "properties.category": category_id,
        "_meta.is_archived": {"$ne": True} 
    }
    cursor = nodes_collection.find(query)
    locations = []
    for doc in cursor:
        doc["_id"] = str(doc.get("_id"))  # Convert ObjectId to string
        locations.append(doc)
    return locations

def get_all_pois(building_id: Optional[str] = None) -> List[Dict]:
    """
    Fetch all ACTIVE POIs, optionally filtered by a specific building ID.
    """
    query = {"_meta.is_archived": {"$ne": True}}
    
    if building_id:
        sanitized_id = building_id.strip().lower()
        # Ensure you use 'properties.building_id' if that's the field in your schema
        query["properties.building_id"] = sanitized_id

    cursor = nodes_collection.find(query)
    pois = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        pois.append(doc)
    return pois

# --- CRUD Functions ---
def add_poi(poi: Dict, created_by: str = None):
    """Add a Point of Interest (POI) to MongoDB."""
    props = poi.get("properties", {})
    if "id" not in props:
        raise ValueError("properties.id is required")

    props["id"] = sanitize_id(props["id"])
    poi["properties"] = props

    poi["_meta"] = {
        "created_by": created_by,
        "created_at": datetime.utcnow().isoformat()
    }

    try:
        result = nodes_collection.insert_one(poi)
        inserted = nodes_collection.find_one({"_id": result.inserted_id})
        inserted["_id"] = str(inserted["_id"]) # Ensure _id is a string on return
        return inserted
    except DuplicateKeyError:
        raise
    
def update_poi(poi_id: str, update_data: Dict, updated_by: str):
    """Update a POI by its properties.id using iterative dot notation."""
    # [Logic for update_poi remains here]
    # ... (all existing logic for preparing update_set_operation, audit, and executing update)
    poi_id = poi_id.strip().lower()

    existing = nodes_collection.find_one({"properties.id": poi_id})
    if not existing:
        raise HTTPException(status_code=404, detail="POI not found")

    update_set_operation = {}
    for key, value in update_data.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                if key == "properties" and sub_key == "id":
                    continue
                update_set_operation[f"{key}.{sub_key}"] = sub_value
        else:
            update_set_operation[key] = value

    update_set_operation["_meta.updated_by"] = updated_by
    update_set_operation["_meta.updated_at"] = datetime.utcnow().isoformat()

    result = nodes_collection.update_one(
        {"properties.id": poi_id},
        {"$set": update_set_operation}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="POI not found after initial check")

    updated = nodes_collection.find_one({"properties.id": poi_id}) 
    updated["_id"] = str(updated["_id"])
    return updated

# --- ACCESSIBILITY UPDATE FUNCTION (MOVED AND FINALIZED) ---
def update_node_accessibility(node_id: str, updates: dict, updated_by: str):
    """Updates specific accessibility fields on a Node (POI)."""
    # [Logic for update_node_accessibility remains here]
    result = nodes_collection.update_one(
        {"properties.id": node_id},
        {
            "$set": {
                **{f"properties.{k}": v for k, v in updates.items()},
                "_meta.updated_by": updated_by,
                "_meta.updated_at": datetime.utcnow().isoformat(),
            }
        }
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found.")

    updated_node = nodes_collection.find_one({"properties.id": node_id})
    updated_node["_id"] = str(updated_node["_id"])
    return updated_node

def delete_poi(poi_id: str, archived_by: str) -> bool:
    """Archives (soft-deletes) a POI by its properties.id."""
    # [Logic for delete_poi remains here]
    poi_id = poi_id.strip().lower()
    
    existing = nodes_collection.find_one({
        "properties.id": poi_id,
        "_meta.is_archived": {"$ne": True}
    })
    
    if not existing:
        return False

    result = nodes_collection.update_one(
        {"properties.id": poi_id},
        {"$set": {
            "_meta.is_archived": True,
            "_meta.archived_at": datetime.utcnow().isoformat(),
            "_meta.archived_by": archived_by
        }}
    )
    return result.modified_count == 1