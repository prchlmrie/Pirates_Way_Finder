"""
Simple script to view all ratings in MongoDB
"""
from app.core.database import db
from bson import json_util
import json

# Get ratings collection
ratings_collection = db["ratings"]

print("=" * 60)
print("RATINGS IN MONGODB")
print("=" * 60)

# Count total ratings
total = ratings_collection.count_documents({})
print(f"\nTotal Ratings: {total}\n")

if total == 0:
    print("No ratings found in the database.")
else:
    # Get all ratings, sorted by newest first
    ratings = list(ratings_collection.find().sort("created_at", -1))
    
    print(f"Showing all {len(ratings)} ratings:\n")
    print("-" * 60)
    
    for i, rating in enumerate(ratings, 1):
        print(f"\n[{i}] Rating ID: {rating.get('_id')}")
        print(f"    Location: {rating.get('location_name')} ({rating.get('location_id')})")
        print(f"    Building: {rating.get('building_name', 'N/A')}")
        print(f"    Rating: {rating.get('rating')}")
        print(f"    Comment: {rating.get('comment', 'No comment')}")
        print(f"    User: {rating.get('user_id', 'Anonymous')}")
        print(f"    Date: {rating.get('created_at')}")
        print("-" * 60)
    
    # Show summary by rating type
    print("\n" + "=" * 60)
    print("SUMMARY BY RATING TYPE")
    print("=" * 60)
    
    pipeline = [
        {"$group": {"_id": "$rating", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    summary = list(ratings_collection.aggregate(pipeline))
    for item in summary:
        print(f"  {item['_id']}: {item['count']} ratings")
    
    # Show summary by building
    print("\n" + "=" * 60)
    print("SUMMARY BY BUILDING")
    print("=" * 60)
    
    pipeline = [
        {"$group": {"_id": "$building_name", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    building_summary = list(ratings_collection.aggregate(pipeline))
    for item in building_summary:
        building = item['_id'] or 'Unknown'
        print(f"  {building}: {item['count']} ratings")

print("\n" + "=" * 60)

