from typing import Annotated, List, Optional
from pydantic import BaseModel, Field
from pydantic.types import StringConstraints

# --- 🎯 Single Source of Truth for Point Geometry ---
class PointGeometry(BaseModel):
    """
    Standard GeoJSON Point geometry validator.
    """
    # Uses Annotated and StringConstraints for strict type checking
    type: Annotated[str, StringConstraints(pattern="^Point$")] = "Point"
    # Ensures coordinates is a list of exactly 2 floats (longitude, latitude)
    coordinates: Annotated[List[float], Field(min_items=2, max_items=2)]

# --- 📏 Single Source of Truth for LineString Geometry ---
class LineStringGeometry(BaseModel):
    """
    Standard GeoJSON LineString geometry validator.
    """
    # Enforces type is exactly "LineString"
    type: Annotated[str, StringConstraints(pattern="^LineString$")] = "LineString"
    # Ensures coordinates is a list of at least two coordinate pairs (paths need a start and end)
    coordinates: Annotated[List[List[float]], Field(min_items=2)]