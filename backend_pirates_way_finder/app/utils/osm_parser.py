import osmium

class OSMHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.nodes = []
        self.ways = []

    def node(self, n):
        self.nodes.append({
            "id": n.id,
            "lat": n.location.lat,
            "lon": n.location.lon,
            "tags": dict(n.tags)
        })

    def way(self, w):
        self.ways.append({
            "id": w.id,
            "nodes": [node.ref for node in w.nodes],
            "tags": dict(w.tags)
        })

def parse_osm(file_path: str):
    handler = OSMHandler()
    handler.apply_file(file_path)
    print(f"Parsed {len(handler.nodes)} nodes and {len(handler.ways)} ways.")
    return handler.nodes, handler.ways