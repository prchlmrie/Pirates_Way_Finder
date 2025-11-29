from typing import Optional, Literal
from pydantic import BaseModel, Field
# Ensure the import path is correct for your setup
from .base_geometry import LineStringGeometry 


# --- Properties for an Edge/Pathway ---
class EdgeProperties(BaseModel):
    id: str = Field(..., description="Unique Edge ID.")
    from_node: str = Field(..., alias="from", description="Starting node ID.")
    to_node: str = Field(..., alias="to", description="Destination node ID.")
    
    type: Literal[
        "corridor", 
        "stairs", 
        "ramp", 
        "pathway"
    ] = Field(..., description="The type of connection.")
    
    environment: Optional[Literal[
        "indoor", 
        "outdoor", 
        "transition"
    ]] = Field(default="transition", description="e.g., 'transition', 'outdoor'.")
    
    accessible: Optional[bool] = Field(default=False)
    building_id: Optional[str] = None
    building_name: Optional[str] = None
    distance: Optional[float] = Field(default=None, description="Auto-computed distance in meters (optional).")


# --- Full GeoJSON Feature Model for Creation/Retrieval ---
class EdgeFeature(BaseModel):
    """The full GeoJSON Feature object, excluding the MongoDB _id."""
    type: str = "Feature"
    geometry: LineStringGeometry
    properties: EdgeProperties

# --- Model for retrieving data from the database (includes _id) ---
class EdgeDB(EdgeFeature):
    """Model used when retrieving from MongoDB, includes the _id."""
    id: Optional[str] = Field(alias="_id", default=None)