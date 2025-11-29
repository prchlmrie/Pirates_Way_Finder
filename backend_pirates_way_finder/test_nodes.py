"""
List all destination nodes from MongoDB
"""
from app.core.database import nodes_collection

print("=== Destination Nodes in MongoDB ===\n")

nodes = list(nodes_collection.find({"_meta.is_archived": {"$ne": True}}))

if not nodes:
    print("No nodes found!")
else:
    print(f"Found {len(nodes)} nodes:\n")
    for node in nodes:
        props = node.get("properties", {})
        coords = node.get("geometry", {}).get("coordinates", [])
        
        name = props.get("name", "Unknown")
        node_id = props.get("id", "no-id")
        category = props.get("category", "no-category")
        
        if coords:
            print(f"  • {name}")
            print(f"    ID: {node_id}")
            print(f"    Category: {category}")
            print(f"    Coordinates: [{coords[0]}, {coords[1]}]")
            print()

