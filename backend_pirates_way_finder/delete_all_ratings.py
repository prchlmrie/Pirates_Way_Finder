"""
Quick script to delete ALL ratings from MongoDB
"""
from app.core.database import db

# Get ratings collection
ratings_collection = db["ratings"]

# Count before deletion
count_before = ratings_collection.count_documents({})
print(f"Found {count_before} ratings in the database.")

if count_before == 0:
    print("No ratings to delete. Database is already empty.")
else:
    # Delete all ratings
    result = ratings_collection.delete_many({})
    print(f"\n✅ Successfully deleted {result.deleted_count} ratings!")
    
    # Verify deletion
    count_after = ratings_collection.count_documents({})
    print(f"Remaining ratings: {count_after}")

print("\nDone! 🎉")

