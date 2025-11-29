from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime, timedelta
from app.core.database import db
from app.core.security import get_current_admin

router = APIRouter()

# Notifications collection
notifications_collection = db["notifications"]

# Create indexes (only if collection is empty or index doesn't exist)
try:
    notifications_collection.create_index("timestamp", -1)
    notifications_collection.create_index("read", 1)
except:
    pass  # Indexes may already exist

def create_notification(
    notification_type: str,
    title: str,
    message: str,
    metadata: dict = None
):
    """Create a notification."""
    notification = {
        "type": notification_type,
        "title": title,
        "message": message,
        "metadata": metadata or {},
        "read": False,
        "timestamp": datetime.utcnow().isoformat(),
    }
    notifications_collection.insert_one(notification)
    return notification

@router.get("/", response_model=List[dict])
def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    current_admin: str = Depends(get_current_admin)
):
    """Get notifications (admin only)."""
    try:
        query = {}
        if unread_only:
            query["read"] = False
        
        notifications = list(
            notifications_collection
            .find(query)
            .sort("timestamp", -1)
            .limit(limit)
        )
        
        # Convert ObjectId to string
        for notif in notifications:
            notif["id"] = str(notif["_id"])
            notif["_id"] = str(notif["_id"])
        
        return notifications
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch notifications: {str(e)}")

@router.post("/{notification_id}/read")
def mark_as_read(notification_id: str, current_admin: str = Depends(get_current_admin)):
    """Mark a notification as read."""
    try:
        from bson import ObjectId
        try:
            obj_id = ObjectId(notification_id)
        except:
            obj_id = notification_id
        
        result = notifications_collection.update_one(
            {"_id": obj_id},
            {"$set": {"read": True, "read_at": datetime.utcnow().isoformat()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return {"success": True, "message": "Notification marked as read"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark notification as read: {str(e)}")

@router.get("/unread/count")
def get_unread_count(current_admin: str = Depends(get_current_admin)):
    """Get count of unread notifications."""
    try:
        count = notifications_collection.count_documents({"read": False})
        return {"unread_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get unread count: {str(e)}")

