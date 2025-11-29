from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime
from app.core.database import db
from app.core.security import get_current_admin

router = APIRouter()

# Audit logs collection
audit_logs_collection = db["audit_logs"]

# Create indexes (only if collection is empty or index doesn't exist)
try:
    audit_logs_collection.create_index("timestamp", -1)
    audit_logs_collection.create_index("admin_email")
    audit_logs_collection.create_index("action_type")
except:
    pass  # Indexes may already exist

# Action types
ACTION_TYPES = {
    "POI_CREATED": "Added POI",
    "POI_UPDATED": "Updated POI",
    "POI_DELETED": "Deleted POI",
    "ACCESSIBILITY_UPDATED": "Updated accessibility",
    "RATING_RECEIVED": "New rating received",
}

def create_audit_log(
    admin_email: str,
    action_type: str,
    description: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    metadata: Optional[dict] = None
):
    """Create an audit log entry."""
    log_entry = {
        "admin_email": admin_email,
        "action_type": action_type,
        "description": description,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "metadata": metadata or {},
        "timestamp": datetime.utcnow().isoformat(),
    }
    audit_logs_collection.insert_one(log_entry)
    return log_entry

@router.get("/", response_model=List[dict])
def get_audit_logs(
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    action_type: Optional[str] = Query(None),
    admin_email: Optional[str] = Query(None),
    current_admin: str = Depends(get_current_admin)
):
    """Get audit logs (admin only)."""
    try:
        query = {}
        
        if action_type:
            query["action_type"] = action_type
        
        if admin_email:
            query["admin_email"] = admin_email
        
        logs = list(
            audit_logs_collection
            .find(query)
            .sort("timestamp", -1)
            .skip(skip)
            .limit(limit)
        )
        
        # Convert ObjectId to string
        for log in logs:
            log["id"] = str(log["_id"])
            log["_id"] = str(log["_id"])
        
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit logs: {str(e)}")

@router.get("/stats")
def get_audit_stats(current_admin: str = Depends(get_current_admin)):
    """Get audit log statistics."""
    try:
        total_logs = audit_logs_collection.count_documents({})
        
        # Count by action type
        pipeline = [
            {"$group": {"_id": "$action_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        action_counts = list(audit_logs_collection.aggregate(pipeline))
        
        return {
            "total_logs": total_logs,
            "by_action_type": {item["_id"]: item["count"] for item in action_counts}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit stats: {str(e)}")

