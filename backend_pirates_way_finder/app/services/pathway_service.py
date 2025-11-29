from app.core.database import edges_collection, nodes_collection
from fastapi import HTTPException
from datetime import datetime
from typing import Dict, List
import math

# --- 🎯 UTILITY FUNCTIONS (KEEP) ---

def compute_distance(coord1, coord2):
    """Compute Euclidean distance between two coordinates (pixels for now)."""
    dx = coord1[0] - coord2[0]
    dy = coord1[1] - coord2[1]
    return round(math.sqrt(dx ** 2 + dy ** 2), 2)

def validate_node_exists(node_id: str):
    """Check if a node exists in the nodes collection."""
    exists = nodes_collection.find_one({"properties.id": node_id})
    if not exists:
        raise HTTPException(status_code=400, detail=f"Node '{node_id}' not found in nodes_collection")

# --- 🎯 EDGE RETRIEVAL (MOVED FROM accessibility_service.py) ---

def get_all_edges(accessible: bool = None) -> List[Dict]:
    """
    Retrieves all edges, optionally filtered by accessibility status.
    This function handles the public GET request and the admin retrieval.
    """
    query = {"_meta.is_archived": {"$ne": True}} # Filter out archived edges by default
    
    if accessible is not None:
        query["properties.accessible"] = accessible

    edges = list(edges_collection.find(query))
    for edge in edges:
        edge["_id"] = str(edge["_id"])
    return edges


# --- EDGE CRUD FUNCTIONS (YOUR EXISTING LOGIC) ---

def add_pathway(edge: Dict, created_by: str):
    """Add a new pathway (edge) between two nodes, including distance computation."""
    props = edge.get("properties", {})
    from_id = props.get("from")
    to_id = props.get("to")

    if not from_id or not to_id:
        raise HTTPException(status_code=400, detail="'from' and 'to' fields are required")

    # Validate nodes exist using the local utility function
    validate_node_exists(from_id)
    validate_node_exists(to_id)

    # Get coordinates and compute distance
    coord1 = nodes_collection.find_one({"properties.id": from_id})["geometry"]["coordinates"]
    coord2 = nodes_collection.find_one({"properties.id": to_id})["geometry"]["coordinates"]
    props["distance"] = props.get("distance") or compute_distance(coord1, coord2)

    # Add metadata
    edge["_meta"] = {
        "created_by": created_by,
        "created_at": datetime.utcnow().isoformat()
    }

    result = edges_collection.insert_one(edge)
    inserted = edges_collection.find_one({"_id": result.inserted_id})
    inserted["_id"] = str(inserted["_id"])
    return inserted

def get_all_pathways() -> List[Dict]:
    """Retrieve all active pathways."""
    edges = list(edges_collection.find({"_meta.is_archived": {"$ne": True}}))
    for e in edges:
        e["_id"] = str(e["_id"])
    return edges

def update_pathway(edge_id: str, update_data: Dict, updated_by: str):
    """Update an existing pathway by its properties.id."""
    existing = edges_collection.find_one({"properties.id": edge_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Edge not found")

    update_fields = {}
    for key, value in update_data.items():
        if isinstance(value, dict):
            for sub_key, sub_val in value.items():
                # Prevent updating properties.id
                if key == "properties" and sub_key == "id":
                    continue
                update_fields[f"{key}.{sub_key}"] = sub_val
        else:
            update_fields[key] = value

    update_fields["_meta.updated_by"] = updated_by
    update_fields["_meta.updated_at"] = datetime.utcnow().isoformat()

    edges_collection.update_one({"properties.id": edge_id}, {"$set": update_fields})
    updated = edges_collection.find_one({"properties.id": edge_id})
    updated["_id"] = str(updated["_id"])
    return updated

def delete_pathway(edge_id: str, archived_by: str) -> bool:
    """Soft delete (archive) a pathway."""
    existing = edges_collection.find_one({
        "properties.id": edge_id,
        "_meta.is_archived": {"$ne": True}
    })
    if not existing:
        return False

    result = edges_collection.update_one(
        {"properties.id": edge_id},
        {"$set": {
            "_meta.is_archived": True,
            "_meta.archived_at": datetime.utcnow().isoformat(),
            "_meta.archived_by": archived_by
        }}
    )
    return result.modified_count == 1


# --- 🎯 EDGE ACCESSIBILITY UPDATES (MOVED FROM accessibility_service.py) ---

def update_edge_accessibility(edge_id: str, accessible: bool, updated_by: str):
    """Toggles the accessibility status of an edge."""
    result = edges_collection.update_one(
        {"properties.id": edge_id},
        {
            "$set": {
                "properties.accessible": accessible,
                "_meta.updated_by": updated_by,
                "_meta.updated_at": datetime.utcnow().isoformat(),
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail=f"Edge '{edge_id}' not found.")

    updated_edge = edges_collection.find_one({"properties.id": edge_id})
    updated_edge["_id"] = str(updated_edge["_id"])
    return updated_edge

def update_edge_notes(edge_id: str, notes: str, updated_by: str):
    """Adds or updates accessibility notes for an edge."""
    result = edges_collection.update_one(
        {"properties.id": edge_id},
        {
            "$set": {
                "properties.notes": notes, # Assuming you have a 'notes' field in your schema
                "_meta.updated_by": updated_by,
                "_meta.updated_at": datetime.utcnow().isoformat(),
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail=f"Edge '{edge_id}' not found.")

    updated_edge = edges_collection.find_one({"properties.id": edge_id})
    updated_edge["_id"] = str(updated_edge["_id"])
    return updated_edge