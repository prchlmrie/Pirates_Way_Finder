from fastapi import APIRouter
from app.services.node_service import get_all_pois
from app.services.pathway_service import get_all_pathways
from typing import Dict, List

router = APIRouter(tags=["Public Map Data"])  # Prefix is set in main.py

@router.get("/nodes", summary="Get all Point features (Nodes/POIs) in GeoJSON format")
def fetch_all_nodes() -> List[Dict]:
    """Retrieves all public map nodes (Points) for rendering or analysis."""
    # Assuming get_all_nodes returns a list of Node objects (dict/GeoJSON features)
    return get_all_pois()

@router.get("/edges", summary="Get all LineString features (Edges/Pathways) in GeoJSON format")
def fetch_all_edges() -> List[Dict]:
    """Retrieves all public map edges (LineStrings) for rendering or analysis."""
    # Assuming get_all_edges returns a list of Edge objects (dict/GeoJSON features)
    return get_all_pathways()
