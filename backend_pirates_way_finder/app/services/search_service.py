from typing import Dict, List, Optional
from app.core.database import nodes_collection
import re
from fastapi import HTTPException
from app.models.node_model import NodeFeature # Import for type hinting/schema reference

def search_locations(
    query: Optional[str] = None, 
    category: Optional[str] = None, 
    building_id: Optional[str] = None
) -> Dict[str, List[Dict]]:
    """
    Performs text search on the MongoDB nodes_collection using indexes for speed.
    
    Filters by:
    1. Text query (on name or tags)
    2. Category (exact match)
    3. Building ID (exact match)
    """
    
    # 1. Base Query: Exclude archived items
    filters = {"_meta.is_archived": {"$ne": True}}

    # 2. Add Building Filter
    if building_id:
        # Assumes building_id field in MongoDB is 'properties.building_id'
        filters["properties.building_id"] = building_id

    # 3. Add Category Filter
    if category:
        # Use case-insensitive exact match for category
        filters["properties.category"] = {"$regex": f"^{re.escape(category)}$", "$options": "i"}

    # 4. Add Text Query Filter (Name OR Tags)
    if query:
        # Use MongoDB's $or for searching across multiple fields (name and tags)
        # using a case-insensitive partial match ($regex)
        regex_query = re.escape(query)
        filters["$or"] = [
            {"properties.name": {"$regex": regex_query, "$options": "i"}},
            {"properties.tags": {"$regex": regex_query, "$options": "i"}}
        ]
    
    # Execute query
    try:
        # Exclude _id on retrieval for cleaner JSON output
        results_cursor = nodes_collection.find(filters, {"_id": 0})
        results = list(results_cursor)
        
    except Exception as e:
        # Handle potential MongoDB errors
        print(f"MongoDB search error: {e}")
        raise HTTPException(status_code=500, detail="Database error during search operation.")

    return {
        "count": len(results),
        "results": results
    }