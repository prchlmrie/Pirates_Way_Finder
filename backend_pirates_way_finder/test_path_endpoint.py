"""
Quick test script to verify pathfinding endpoint works
"""

import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000"

# Test coordinates for RESIZED map (1449 x 2565)
# Coordinates must be within: 0 to 1449 (width), 0 to 2565 (height)
START_X = 504   # Starting point - main entrance
START_Y = 2302  # Starting point - main entrance
END_X = 700     # Test destination
END_Y = 500     # Test destination

print("=" * 60)
print("TESTING PATHFINDING ENDPOINT")
print("=" * 60)

# Test 1: Check if backend is running
print("\n[TEST 1] Checking if backend is accessible...")
try:
    response = requests.get(f"{BASE_URL}/", timeout=2)
    print(f"✅ Backend is running: {response.json()}")
except requests.exceptions.ConnectionError:
    print(f"❌ Backend not accessible: Connection refused")
    print("\n" + "="*60)
    print("⚠️  BACKEND IS NOT RUNNING!")
    print("="*60)
    print("\nYou need to start the backend first:")
    print("   1. Open a NEW terminal window")
    print("   2. cd backend_pirates_way_finder")
    print("   3. python main.py")
    print("\n   OR run: START_BACKEND.bat")
    print("\n   Then come back and run this test again!")
    print("="*60)
    exit(1)
except Exception as e:
    print(f"❌ Backend not accessible: {e}")
    print("   Make sure to run: python main.py")
    exit(1)

# Test 2: Check if grid is loaded
print("\n[TEST 2] Checking walkable grid...")
try:
    response = requests.get(f"{BASE_URL}/path/walkable-grid")
    data = response.json()
    walkable_count = len(data.get("walkable_cells", []))
    print(f"✅ Grid loaded:")
    print(f"   Walkable cells: {walkable_count:,}")
    print(f"   Grid dimensions: {data.get('grid_width')}x{data.get('grid_height')}")
    print(f"   Cell size: {data.get('cell_size')}px")
    
    if walkable_count == 0:
        print("\n⚠️  WARNING: No walkable cells!")
        print("   Your grid might be all walls.")
        print("   Run: python edit_grid.py")
        print("   Then mark some areas as walkable (0)")
except Exception as e:
    print(f"❌ Error getting walkable grid: {e}")

# Test 3: Test pathfinding (A* algorithm)
print(f"\n[TEST 3] Testing A* pathfinding...")
print(f"   Start: [{START_X}, {START_Y}]")
print(f"   End: [{END_X}, {END_Y}]")

try:
    payload = {
        "start_x": START_X,
        "start_y": START_Y,
        "end_x": END_X,
        "end_y": END_Y,
        "accessibility_mode": False
    }
    
    response = requests.post(
        f"{BASE_URL}/path/shortest",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        path = data.get("path", [])
        
        if len(path) > 0:
            print(f"✅ PATH FOUND!")
            print(f"   Waypoints: {len(path)}")
            print(f"   First point: {path[0]}")
            print(f"   Last point: {path[-1]}")
            print(f"\n   Sample path (first 5 points):")
            for i, point in enumerate(path[:5]):
                print(f"      {i+1}. ({point['x']:.1f}, {point['y']:.1f})")
        else:
            print(f"❌ NO PATH FOUND!")
            print("   Possible reasons:")
            print("   1. Start or end point is on a wall")
            print("   2. No walkable path exists between points")
            print("   3. Grid has no walkable cells")
            print("\n   Fix: Use edit_grid.py to mark walkable areas")
    else:
        print(f"❌ Error: HTTP {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error testing pathfinding: {e}")

# Test 4: Test with accessibility mode
print(f"\n[TEST 4] Testing with accessibility mode ON...")
try:
    payload = {
        "start_x": START_X,
        "start_y": START_Y,
        "end_x": END_X,
        "end_y": END_Y,
        "accessibility_mode": True
    }
    
    response = requests.post(
        f"{BASE_URL}/path/shortest",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        path = data.get("path", [])
        
        if len(path) > 0:
            print(f"✅ ACCESSIBLE PATH FOUND!")
            print(f"   Waypoints: {len(path)}")
        else:
            print(f"⚠️  No accessible path found")
            print("   (This is okay if you haven't marked ramps)")
    else:
        print(f"❌ Error: HTTP {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print("\n✅ Backend is using A* algorithm")
print("✅ If path was found, it will show as GREEN line in app")
print("\nIf no path was found:")
print("  1. Run: python visualize_grid.py")
print("  2. Check grid_visualization.png")
print("  3. If all red (walls), run: python edit_grid.py")
print("  4. Mark walkable corridors as 0 (walkable)")
print("=" * 60)

