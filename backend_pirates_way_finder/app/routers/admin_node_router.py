from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.models.node_model import NodeFeature  # 🎯 Renamed from POICreate
from app.services.node_service import add_poi, update_poi, get_all_pois, delete_poi, update_node_accessibility
# 🎯 Import the node accessibility service needed for the moved route
from app.core.security import get_current_admin
from app.routers.audit_log_router import create_audit_log
from app.routers.notification_router import create_notification
from pymongo.errors import DuplicateKeyError
from typing import Optional, List, Dict


router = APIRouter(tags=["Admin POI Management"])  # Prefix is applied in main.py

# --- 2.1 ADD LOCATION (POI) ---
@router.post("/", status_code=201, summary="Add a new Point of Interest (Node)")
def create_poi(poi: NodeFeature, current_admin: str = Depends(get_current_admin)): # Use NodeFeature
    """Add a new POI (admin only)."""
    try:
        poi_dict = poi.model_dump(by_alias=True)
        inserted = add_poi(poi_dict, created_by=current_admin)
        if inserted and "_id" in inserted:
            inserted["_id"] = str(inserted["_id"])
        
        # Create audit log
        poi_name = poi_dict.get("properties", {}).get("name", poi_dict.get("properties", {}).get("id", "Unknown"))
        create_audit_log(
            admin_email=current_admin,
            action_type="POI_CREATED",
            description=f"Added POI: {poi_name}",
            entity_type="POI",
            entity_id=poi_dict.get("properties", {}).get("id"),
            metadata={"poi_name": poi_name}
        )
        
        # Create notification
        create_notification(
            notification_type="POI_CREATED",
            title="New POI Added",
            message=f"POI '{poi_name}' has been added",
            metadata={"poi_id": poi_dict.get("properties", {}).get("id")}
        )
        
        return {"success": True, "message": "POI added successfully", "poi": inserted}
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="POI id already exists")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

# --- 2.2 EDIT LOCATION (POI) ---
@router.patch("/{node_id}", summary="Update general information for a Node/POI") # 🎯 Cleaner path
def patch_poi(node_id: str, updated_data: dict, current_admin: str = Depends(get_current_admin)):
    """Patch a POI by its properties.id (admin only)."""
    try:
        updated_poi = update_poi(node_id, updated_data, current_admin)
        
        # Create audit log
        poi_name = updated_poi.get("properties", {}).get("name", node_id)
        create_audit_log(
            admin_email=current_admin,
            action_type="POI_UPDATED",
            description=f"Updated POI: {poi_name}",
            entity_type="POI",
            entity_id=node_id,
            metadata={"poi_name": poi_name, "updated_fields": list(updated_data.keys())}
        )
        
        # Create notification
        create_notification(
            notification_type="POI_UPDATED",
            title="POI Updated",
            message=f"POI '{poi_name}' has been modified",
            metadata={"poi_id": node_id}
        )
        
        return {"success": True, "message": "POI updated successfully", "poi": updated_poi}
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error during update")

# --- 4.1 UPDATE NODE ACCESSIBILITY (MOVED FROM admin_accessibility_router) ---
@router.patch("/{node_id}/accessibility-info", summary="Update accessibility information for a Node/POI")
def patch_node_accessibility(
    node_id: str,
    updates: dict, # Ideally, this should use a Pydantic model for updates too!
    current_admin: str = Depends(get_current_admin)
):
    """Update accessibility specific info for a node (e.g., accessible: true/false, notes)."""
    updated_node = update_node_accessibility(node_id, updates, current_admin)
    
    # Create audit log
    poi_name = updated_node.get("properties", {}).get("name", node_id)
    create_audit_log(
        admin_email=current_admin,
        action_type="ACCESSIBILITY_UPDATED",
        description=f"Updated accessibility for: {poi_name}",
        entity_type="POI",
        entity_id=node_id,
        metadata={"poi_name": poi_name, "accessibility_updates": updates}
    )
    
    # Create notification
    create_notification(
        notification_type="ACCESSIBILITY_UPDATED",
        title="Accessibility Updated",
        message=f"Accessibility for '{poi_name}' has been modified",
        metadata={"poi_id": node_id}
    )
    
    return {
        "success": True,
        "message": f"Accessibility info updated for node '{node_id}'.",
        "node": updated_node
    }

# --- 2.3 REMOVE LOCATION (POI) ---
@router.delete("/{node_id}", status_code=status.HTTP_200_OK, summary="Archive (Soft-Delete) a Node/POI") # 🎯 Cleaner path
def delete_poi_node(node_id: str, current_admin: str = Depends(get_current_admin)):
    """Archive (Soft-Delete) a POI by its properties.id (admin only)."""
    try:
        # Get POI name before deletion for audit log
        from app.core.database import nodes_collection
        existing = nodes_collection.find_one({"properties.id": node_id})
        poi_name = existing.get("properties", {}).get("name", node_id) if existing else node_id
        
        was_archived = delete_poi(node_id, archived_by=current_admin)
        if not was_archived:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"POI with ID '{node_id}' not found or already archived.")
        
        # Create audit log
        create_audit_log(
            admin_email=current_admin,
            action_type="POI_DELETED",
            description=f"Deleted POI: {poi_name}",
            entity_type="POI",
            entity_id=node_id,
            metadata={"poi_name": poi_name}
        )
        
        # Create notification
        create_notification(
            notification_type="POI_DELETED",
            title="POI Deleted",
            message=f"POI '{poi_name}' has been deleted",
            metadata={"poi_id": node_id}
        )
        
        return {"success": True, "message": f"POI with ID '{node_id}' has been successfully archived."}
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="Internal server error during archival.")

# --- 2.X GET ALL LOCATIONS (READ) ---
@router.get("/all", response_model=List[Dict], summary="Retrieve all POI nodes, optionally filtered by building")
def get_all_nodes(building_id: Optional[str] = Query(None, description="Optional filter by building ID")):
    """Retrieve all Point of Interest (POI) nodes."""
    # (Existing logic...)
    try:
        pois = get_all_pois(building_id=building_id)
        if not pois and building_id:
            raise HTTPException(status_code=404, detail=f"No POIs found for building ID: {building_id}")
        return pois
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")