from typing import List, Optional, Literal
from pydantic import BaseModel, Field
# Ensure the import path is correct for your setup
from .base_geometry import PointGeometry 

# --- Properties for the Node/Point of Interest (POI) ---
class NodeProperties(BaseModel):
    id: str = Field(..., description="Unique Node ID (e.g., 'lecafe').")
    name: Optional[str] = None
   
    type: Literal[
        "room", 
        "intersection", 
        "corridor_node", 
        "stairs_entry", 
        "stairs_exit", 
        "ramp_entry", 
        "ramp_exit", 
        "elevator"
    ] = Field(..., description="The functional type of the node.")
   
    category: Optional[Literal[
        "office", 
        "classroom", 
        "laboratory", 
        "amenity"
    ]] = None
    floor: Optional[int] = None
    
    environment: Optional[Literal[
        "indoor", 
        "outdoor", 
        "transition"
    ]] = Field(default="indoor", description="e.g., 'indoor', 'outdoor'.")
    
    accessible: Optional[bool] = Field(default=False)
    tags: Optional[List[str]] = Field(default=[], description="Keywords for search.")
    building_id: Optional[str] = None
    building_name: Optional[str] = None
    
# --- Full GeoJSON Feature Model for Creation/Retrieval ---
class NodeFeature(BaseModel):
    """The full GeoJSON Feature object, excluding the MongoDB _id."""
    type: str = "Feature"
    geometry: PointGeometry
    properties: NodeProperties

# --- Model for retrieving data from the database (includes _id) ---
class NodeDB(NodeFeature):
    """Model used when retrieving from MongoDB, includes the _id."""
    # Note: _id is typically handled by the driver, but can be modeled for clarity
    id: Optional[str] = Field(alias="_id", default=None)