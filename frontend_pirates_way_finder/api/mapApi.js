// API URL Configuration
// For Android Emulator: Use 10.0.2.2 to access host machine's localhost
// For iOS Simulator: Use localhost (works directly)
// For Physical Device: Use your computer's IP address (find with ipconfig/ifconfig)
// For Web Browser: Use localhost

import { Platform } from 'react-native';

const getBaseUrl = () => {
  // Check for environment variable first
  if (process.env.EXPO_PUBLIC_API_URL) {
    return process.env.EXPO_PUBLIC_API_URL;
  }
  
  // Auto-detect platform
  if (Platform.OS === 'android') {
    // Android emulator uses 10.0.2.2 to access host machine's localhost
    return "http://10.0.2.2:8000";
  } else if (Platform.OS === 'ios') {
    // iOS simulator can use localhost directly
    return "http://localhost:8000";
  } else {
    // Web browser
    return "http://localhost:8000";
  }
};

const BASE_URL = getBaseUrl();

export async function getNodes() {
  try {
    console.log(`🔍 Fetching nodes from: ${BASE_URL}/map/nodes`);
    const response = await fetch(`${BASE_URL}/map/nodes`);
    console.log(`📡 Response status: ${response.status} ${response.statusText}`);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ HTTP Error ${response.status}:`, errorText);
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }
    
    const data = await response.json();
    console.log(`✅ Successfully fetched ${data.length} nodes`);
    return data;
  } catch (err) {
    console.error("❌ Error fetching nodes:", err.message);
    console.error("Full error:", err);
    alert(`Failed to fetch nodes: ${err.message}\n\nAPI URL: ${BASE_URL}/map/nodes\n\nCheck console for details.`);
    return [];
  }
}

export async function getEdges() {
  try {
    console.log(`🔍 Fetching edges from: ${BASE_URL}/map/edges`);
    const response = await fetch(`${BASE_URL}/map/edges`);
    console.log(`📡 Response status: ${response.status} ${response.statusText}`);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ HTTP Error ${response.status}:`, errorText);
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }
    
    const data = await response.json();
    console.log(`✅ Successfully fetched ${data.length} edges`);
    return data;
  } catch (err) {
    console.error("❌ Error fetching edges:", err.message);
    console.error("Full error:", err);
    return [];
  }
}

/**
 * Calculate shortest path using grid-based Dijkstra pathfinding
 * @param {number} startX - Starting X pixel coordinate
 * @param {number} startY - Starting Y pixel coordinate  
 * @param {number} endX - Ending X pixel coordinate
 * @param {number} endY - Ending Y pixel coordinate
 * @param {boolean} accessibilityMode - If true, avoid stairs and use ramps
 * @returns {Promise<Array>} Array of {x, y} path coordinates
 */
export async function getShortestPath(startX, startY, endX, endY, accessibilityMode = false) {
  try {
    console.log(`🗺️ Calculating grid-based path from [${startX}, ${startY}] to [${endX}, ${endY}]`);
    console.log(`♿ Accessibility mode: ${accessibilityMode ? 'ON (avoiding stairs)' : 'OFF'}`);
    
    const response = await fetch(`${BASE_URL}/path/shortest`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        start_x: Math.round(startX),
        start_y: Math.round(startY),
        end_x: Math.round(endX),
        end_y: Math.round(endY),
        accessibility_mode: accessibilityMode,
      }),
    });
    
    console.log(`📡 Pathfinding response: ${response.status} ${response.statusText}`);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ Pathfinding error ${response.status}:`, errorText);
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }
    
    const data = await response.json();
    console.log(`✅ Path calculated with ${data.path.length} waypoints`);
    console.log(`📝 Instructions: ${data.instructions?.length || 0} steps`);
    console.log(`📏 Distance: ${data.distance_meters}m, Time: ${data.estimated_time_minutes}min`);
    
    // Return full response with path, instructions, distance, and time
    return {
      path: data.path || [],
      instructions: data.instructions || [],
      distance_meters: data.distance_meters || 0,
      estimated_time_minutes: data.estimated_time_minutes || 0
    };
  } catch (err) {
    console.error("❌ Error calculating path:", err.message);
    console.error("Full error:", err);
    return {
      path: [],
      instructions: [],
      distance_meters: 0,
      estimated_time_minutes: 0
    };
  }
}

/**
 * Get all walkable paths/corridors from the grid
 * @returns {Promise<Array>} Array of walkable cell coordinates
 */
export async function getWalkableGrid() {
  try {
    console.log(`🗺️ Fetching walkable grid...`);
    
    const response = await fetch(`${BASE_URL}/path/walkable-grid`);
    console.log(`📡 Walkable grid response: ${response.status} ${response.statusText}`);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ Error ${response.status}:`, errorText);
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }
    
    const data = await response.json();
    console.log(`✅ Fetched ${data.walkable_cells?.length || 0} walkable cells`);
    return data.walkable_cells || [];
  } catch (err) {
    console.error("❌ Error fetching walkable grid:", err.message);
    return [];
  }
}






