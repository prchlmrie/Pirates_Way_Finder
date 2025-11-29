"""
Script to remove ratings from MongoDB
"""
from app.core.database import db
from bson import ObjectId

# Get ratings collection
ratings_collection = db["ratings"]

print("=" * 60)
print("REMOVE RATINGS FROM MONGODB")
print("=" * 60)

# Count total ratings
total = ratings_collection.count_documents({})
print(f"\nCurrent Total Ratings: {total}\n")

if total == 0:
    print("No ratings to remove.")
    exit()

# Show current ratings
print("Current Ratings:")
print("-" * 60)
ratings = list(ratings_collection.find().sort("created_at", -1))
for i, rating in enumerate(ratings, 1):
    print(f"[{i}] {rating.get('location_name')} - {rating.get('rating')} - {rating.get('created_at')}")

print("\n" + "=" * 60)
print("OPTIONS:")
print("=" * 60)
print("1. Remove ALL ratings")
print("2. Remove by rating ID")
print("3. Remove by location")
print("4. Cancel")
print("=" * 60)

choice = input("\nEnter your choice (1-4): ").strip()

if choice == "1":
    # Remove all ratings
    confirm = input("\n⚠️  Are you SURE you want to delete ALL ratings? (yes/no): ").strip().lower()
    if confirm == "yes":
        result = ratings_collection.delete_many({})
        print(f"\n✅ Successfully deleted {result.deleted_count} ratings!")
    else:
        print("\n❌ Cancelled. No ratings were deleted.")

elif choice == "2":
    # Remove by ID
    rating_id = input("\nEnter the rating ID (ObjectId) to delete: ").strip()
    try:
        obj_id = ObjectId(rating_id)
        result = ratings_collection.delete_one({"_id": obj_id})
        if result.deleted_count > 0:
            print(f"\n✅ Successfully deleted rating with ID: {rating_id}")
        else:
            print(f"\n❌ No rating found with ID: {rating_id}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

elif choice == "3":
    # Remove by location
    location_name = input("\nEnter the location name to delete ratings for: ").strip()
    confirm = input(f"⚠️  Delete ALL ratings for '{location_name}'? (yes/no): ").strip().lower()
    if confirm == "yes":
        result = ratings_collection.delete_many({"location_name": location_name})
        print(f"\n✅ Successfully deleted {result.deleted_count} ratings for '{location_name}'!")
    else:
        print("\n❌ Cancelled. No ratings were deleted.")

elif choice == "4":
    print("\n❌ Cancelled. No ratings were deleted.")

else:
    print("\n❌ Invalid choice.")

# Show final count
final_count = ratings_collection.count_documents({})
print(f"\n" + "=" * 60)
print(f"Final Total Ratings: {final_count}")
print("=" * 60)

