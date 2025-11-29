from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models.edge_model import EdgeFeature # 🎯 Renamed from PathwayCreate
from app.services.pathway_service import add_pathway, get_all_pathways, update_pathway, delete_pathway, update_edge_accessibility, update_edge_notes
# 🎯 Import edge-specific services needed for the moved routes
from app.core.security import get_current_admin
from typing import Optional

router = APIRouter(tags=["Admin Pathway Management"])  # Prefix is applied in main.py

# --- 3.0 CREATE PATHWAY ---
@router.post("/", status_code=201, summary="Add a new Edge/Pathway")
def create_pathway(pathway: EdgeFeature, current_admin: str = Depends(get_current_admin)): # Use EdgeFeature
    try:
        inserted = add_pathway(pathway.model_dump(by_alias=True), created_by=current_admin)
        return {"success": True, "message": "Pathway added successfully", "pathway": inserted}
    except HTTPException as e:
        raise e
    except Exception as e:
        # Better error handling: use 500 status for unexpected server errors
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# --- 3.0 GET ALL PATHWAYS (READ) ---
@router.get("/all", summary="Retrieve all Edges/Pathways")
def fetch_pathways(current_admin: str = Depends(get_current_admin)):
    """Retrieve all Edges. Note: The /all endpoint from the old accessibility router is redundant and removed."""
    edges = get_all_pathways()
    return edges

# --- 3.0 UPDATE PATHWAY (General Patch) ---
@router.patch("/{edge_id}", summary="Update general information for an Edge/Pathway") # 🎯 Cleaner path
def modify_pathway(edge_id: str, update_data: dict, current_admin: str = Depends(get_current_admin)):
    """Update general pathway data (type, building, etc.)."""
    try:
        updated = update_pathway(edge_id, update_data, updated_by=current_admin)
        return {"success": True, "message": "Pathway updated successfully", "pathway": updated}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# --- 4.1 TOGGLE EDGE ACCESSIBILITY (MOVED FROM admin_accessibility_router) ---
@router.patch("/{edge_id}/accessibility", summary="Toggle accessibility status for an Edge/Pathway")
def patch_edge_accessibility(
    edge_id: str,
    accessible: bool = Query(..., description="Set to true or false"),
    current_admin: str = Depends(get_current_admin)
):
    """Update the accessible boolean field for an Edge/Pathway."""
    updated_edge = update_edge_accessibility(edge_id, accessible, current_admin)
    return {
        "success": True,
        "message": f"Edge '{edge_id}' accessibility updated to {accessible}.",
        "edge": updated_edge
    }

# --- 4.1 ADD OR EDIT ACCESSIBILITY NOTES (MOVED FROM admin_accessibility_router) ---
@router.patch("/{edge_id}/notes", summary="Add or edit accessibility notes for an Edge/Pathway")
def patch_edge_notes(
    edge_id: str,
    notes: str = Query(..., description="Accessibility-related notes or remarks"),
    current_admin: str = Depends(get_current_admin)
):
    """Add or edit the accessibility notes/remarks field for an Edge/Pathway."""
    updated_edge = update_edge_notes(edge_id, notes, current_admin)
    return {
        "success": True,
        "message": f"Accessibility note updated for edge '{edge_id}'.",
        "edge": updated_edge
    }

# --- 3.0 DELETE PATHWAY ---
@router.delete("/{edge_id}", status_code=status.HTTP_200_OK, summary="Archive (Soft-Delete) an Edge/Pathway") # 🎯 Cleaner path
def remove_pathway(edge_id: str, current_admin: str = Depends(get_current_admin)):
    """Archive (Soft-Delete) an Edge/Pathway."""
    success = delete_pathway(edge_id, archived_by=current_admin)
    if not success:
        raise HTTPException(status_code=404, detail=f"Pathway '{edge_id}' not found or already archived.")
    return {"success": True, "message": f"Pathway '{edge_id}' archived successfully."}