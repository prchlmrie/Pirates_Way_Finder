from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.core.database import db
from app.routers.notification_router import create_notification

router = APIRouter()

# Ratings collection
ratings_collection = db["ratings"]

# Create index for faster queries
ratings_collection.create_index("location_id")
ratings_collection.create_index("created_at")

# Rating model
class RatingCreate(BaseModel):
    location_id: str
    location_name: str
    building_name: Optional[str] = None
    rating: str  # 'BAD', 'NOT BAD', 'GOOD'
    comment: Optional[str] = None
    user_id: Optional[str] = None  # Optional for anonymous ratings

class RatingResponse(BaseModel):
    id: str
    location_id: str
    location_name: str
    building_name: Optional[str]
    rating: str
    comment: Optional[str]
    user_id: Optional[str]
    created_at: str

@router.post("/", status_code=201)
def create_rating(rating: RatingCreate):
    """Create a new rating for a location."""
    try:
        rating_doc = {
            "location_id": rating.location_id,
            "location_name": rating.location_name,
            "building_name": rating.building_name,
            "rating": rating.rating,
            "comment": rating.comment or "",
            "user_id": rating.user_id or f"anonymous_{datetime.utcnow().timestamp()}",
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = ratings_collection.insert_one(rating_doc)
        rating_doc["id"] = str(result.inserted_id)
        rating_doc["_id"] = str(result.inserted_id)
        
        # Create notification for new rating
        create_notification(
            notification_type="RATING_RECEIVED",
            title="New Rating Received",
            message=f"New {rating.rating} rating for {rating.location_name}",
            metadata={
                "location_id": rating.location_id,
                "location_name": rating.location_name,
                "rating": rating.rating
            }
        )
        
        return {
            "success": True,
            "message": "Rating submitted successfully",
            "rating": rating_doc
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create rating: {str(e)}")

@router.get("/", response_model=List[dict])
def get_all_ratings(
    location_id: Optional[str] = Query(None, description="Filter by location ID"),
    building_name: Optional[str] = Query(None, description="Filter by building name")
):
    """Get all ratings, optionally filtered by location_id or building_name."""
    try:
        query = {}
        
        if location_id:
            query["location_id"] = location_id
        
        if building_name:
            query["building_name"] = building_name
        
        ratings = list(ratings_collection.find(query).sort("created_at", -1))
        
        # Convert ObjectId to string
        for rating in ratings:
            rating["id"] = str(rating["_id"])
            rating["_id"] = str(rating["_id"])
        
        return ratings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ratings: {str(e)}")

@router.get("/by-location/{location_id}")
def get_ratings_by_location(location_id: str):
    """Get all ratings for a specific location."""
    try:
        ratings = list(ratings_collection.find({"location_id": location_id}).sort("created_at", -1))
        
        for rating in ratings:
            rating["id"] = str(rating["_id"])
            rating["_id"] = str(rating["_id"])
        
        return {
            "location_id": location_id,
            "count": len(ratings),
            "ratings": ratings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ratings: {str(e)}")

@router.get("/locations")
def get_locations_with_ratings():
    """Get all unique locations that have ratings, grouped by location."""
    try:
        pipeline = [
            {
                "$group": {
                    "_id": "$location_id",
                    "location_name": {"$first": "$location_name"},
                    "building_name": {"$first": "$building_name"},
                    "rating_count": {"$sum": 1},
                    "latest_rating": {"$max": "$created_at"}
                }
            },
            {
                "$sort": {"latest_rating": -1}
            }
        ]
        
        locations = list(ratings_collection.aggregate(pipeline))
        
        return {
            "count": len(locations),
            "locations": locations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch locations: {str(e)}")

