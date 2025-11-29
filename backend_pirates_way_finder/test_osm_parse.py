from app.utils.osm_parser import parse_osm

# Replace this with your actual file name
osm_file = "map.osm"

nodes, ways = parse_osm(osm_file)

print(f"\nParsed {len(nodes)} nodes and {len(ways)} ways.\n")

print("=== First 5 nodes ===")
for n in nodes[:5]:
    print(n)

print("\n=== First 3 ways ===")
for w in ways[:3]:
    print(w)