from app.core.database import nodes_collection

# Find the FeatureCollection document
feature_collection = nodes_collection.find_one({ "type": "FeatureCollection" })

# Insert each feature as a separate document
if feature_collection and "features" in feature_collection:
    for feature in feature_collection["features"]:
        nodes_collection.insert_one(feature)

# Optionally delete the original FeatureCollection
nodes_collection.delete_one({ "_id": feature_collection["_id"] })

print("✅ Split FeatureCollection into individual node documents.")
