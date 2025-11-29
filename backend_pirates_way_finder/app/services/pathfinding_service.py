import networkx as nx
from app.core.database import nodes_collection, edges_collection
import math
import logging
logger = logging.getLogger(__name__)

def ensure_nodes_are_split():
    """Splits FeatureCollection into individual node documents if needed."""
    fc = nodes_collection.find_one({ "type": "FeatureCollection" })
    if fc and "features" in fc:
        for feature in fc["features"]:
            nodes_collection.insert_one(feature)
        nodes_collection.delete_one({ "_id": fc["_id"] })
        print("✅ Split FeatureCollection into individual node documents.")

def ensure_edges_are_split():
    fc = edges_collection.find_one({ "type": "FeatureCollection" })
    if fc and "features" in fc:
        for feature in fc["features"]:
            edges_collection.insert_one(feature)
        edges_collection.delete_one({ "_id": fc["_id"] })
        print("✅ Split FeatureCollection into individual edge documents.")

def build_graph(accessible_only: bool = False):
    ensure_nodes_are_split()
    ensure_edges_are_split()

    G = nx.Graph()
    nodes = list(nodes_collection.find())
    node_coords = {
        n["properties"]["id"]: n["geometry"]["coordinates"]
        for n in nodes
        if "properties" in n and "geometry" in n and "coordinates" in n["geometry"]
    }

    raw_edges = list(edges_collection.find({}))
    edges = [e for e in raw_edges if "properties" in e and "geometry" in e]

    for edge in edges:
        props = edge["properties"]
        from_id = props.get("from")
        to_id = props.get("to")
        accessible = props.get("accessible", True)

        if accessible_only and not accessible:
            continue  # Skip non-accessible edges

        coord1 = node_coords.get(from_id)
        coord2 = node_coords.get(to_id)
        if not coord1 or not coord2:
            continue

        dx = coord1[0] - coord2[0]
        dy = coord1[1] - coord2[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)

        G.add_edge(from_id, to_id, weight=distance, accessible=accessible)

    return G


def generate_turn_instructions(path, node_coords, pixel_to_meter=0.02):
    """
    Given a list of node IDs (path) and their coordinates,
    generate human-readable turn-by-turn instructions.
    """
    if len(path) < 2:
        return ["You are already at your destination."]

    instructions = []

    for i in range(len(path) - 1):
        start = path[i]
        end = path[i + 1]
        start_coord = node_coords.get(start)
        end_coord = node_coords.get(end)

        if not start_coord or not end_coord:
            continue

        # compute segment distance
        dx = end_coord[0] - start_coord[0]
        dy = end_coord[1] - start_coord[1]
        distance_px = math.sqrt(dx ** 2 + dy ** 2)
        distance_m = distance_px * pixel_to_meter

        # if this is the first step
        if i == 0:
            instructions.append(f"Start at {start.replace('_', ' ').title()}. Go straight for {round(distance_m, 1)} meters.")
            continue

        # if not first step, compute turn
        prev = path[i - 1]
        prev_coord = node_coords.get(prev)
        if not prev_coord:
            continue

        v1 = (start_coord[0] - prev_coord[0], start_coord[1] - prev_coord[1])
        v2 = (end_coord[0] - start_coord[0], end_coord[1] - start_coord[1])

        # dot and cross for angle detection
        dot = v1[0]*v2[0] + v1[1]*v2[1]
        cross = v1[0]*v2[1] - v1[1]*v2[0]
        angle = math.degrees(math.atan2(cross, dot))

        # decide direction
        if angle > 15:
            turn = "Turn left"
        elif angle < -15:
            turn = "Turn right"
        else:
            turn = "Go straight"

        if i == len(path) - 2:
            instructions.append(f"{turn} and arrive at {end.replace('_', ' ').title()}.")
        else:
            instructions.append(f"{turn} for about {round(distance_m, 1)} meters toward {end.replace('_', ' ').title()}.")

    return instructions

def find_shortest_path(start_id: str, end_id: str, accessible_only: bool = False):
    G = build_graph(accessible_only=accessible_only)

    if start_id not in G or end_id not in G:
        return {"error": "Invalid node ID(s)."}

    try:
        path = nx.dijkstra_path(G, source=start_id, target=end_id, weight="weight")
        total_distance = nx.dijkstra_path_length(G, source=start_id, target=end_id, weight="weight")

        # distance + time
        PIXEL_TO_METER = 0.02
        AVERAGE_WALK_SPEED = 1.4
        distance_meters = total_distance * PIXEL_TO_METER
        time_seconds = distance_meters / AVERAGE_WALK_SPEED

        # create node lookup again for instruction generator
        nodes = list(nodes_collection.find())
        node_coords = {
            n["properties"]["id"]: n["geometry"]["coordinates"]
            for n in nodes
            if "properties" in n and "geometry" in n and "coordinates" in n["geometry"]
        }

        # 🧭 generate turn-by-turn instructions
        instructions = generate_turn_instructions(path, node_coords, PIXEL_TO_METER)

        return {
            "path": path,
            "distance_meters": round(distance_meters, 2),
            "estimated_time_seconds": round(time_seconds, 1),
            "estimated_time_minutes": round(time_seconds / 60, 2),
            "instructions": instructions
        }

    except nx.NetworkXNoPath:
        return {"error": "No path found between these nodes."}
