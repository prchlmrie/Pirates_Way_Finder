import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DBNAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

# Collections
nodes_collection = db["Floor1Nodes"]
edges_collection = db["Floor1Edges"]

# after you define nodes_collection = db["nodes"]
nodes_collection.create_index("properties.id", unique=True)
# optionally index category and tags for search
nodes_collection.create_index("properties.category")
nodes_collection.create_index("properties.tags")