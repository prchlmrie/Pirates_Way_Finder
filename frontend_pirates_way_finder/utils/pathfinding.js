/**
 * Pathfinding Utility using Dijkstra's Algorithm
 * 
 * Finds the shortest path between two nodes in a graph (map),
 * with optional accessibility filtering.
 */

/**
 * Build a graph (adjacency list) from nodes and edges
 * @param {Array} nodes - Array of node objects
 * @param {Array} edges - Array of edge objects
 * @param {Boolean} accessibleOnly - If true, only include accessible edges
 * @returns {Object} Graph object with adjacency list and node coordinate map
 */
export function buildGraph(nodes, edges, accessibleOnly = false) {
  const graph = {}; // adjacency list: { nodeId: [{to: nodeId, distance: num}, ...] }
  const nodeCoords = {}; // map nodeId to coordinates for drawing paths
  
  // Build node coordinates map
  nodes.forEach(node => {
    const nodeId = node?.properties?.id || node?.id;
    const coords = node?.geometry?.coordinates || [0, 0];
    if (nodeId) {
      nodeCoords[nodeId] = coords;
      graph[nodeId] = []; // initialize adjacency list
    }
  });
  
  // Build adjacency list from edges
  edges.forEach(edge => {
    const from = edge?.properties?.from;
    const to = edge?.properties?.to;
    const accessible = edge?.properties?.accessible || false;
    const edgeType = edge?.properties?.type || 'corridor';
    
    // Skip if nodes don't exist
    if (!from || !to || !graph[from] || !graph[to]) {
      return;
    }
    
    // Skip if accessibility filter is on and edge is not accessible
    if (accessibleOnly && !accessible) {
      console.log(`⚠️ Skipping inaccessible edge: ${from} → ${to} (type: ${edgeType})`);
      return;
    }
    
    // Calculate distance (Euclidean distance between coordinates)
    const fromCoords = nodeCoords[from];
    const toCoords = nodeCoords[to];
    const distance = Math.sqrt(
      Math.pow(toCoords[0] - fromCoords[0], 2) +
      Math.pow(toCoords[1] - fromCoords[1], 2)
    );
    
    // Add bidirectional edges (can go both ways)
    graph[from].push({ to, distance, accessible, type: edgeType });
    graph[to].push({ to: from, distance, accessible, type: edgeType });
  });
  
  console.log(`📊 Graph built: ${Object.keys(graph).length} nodes, ${edges.length} edges`);
  if (accessibleOnly) {
    console.log(`♿ Accessibility mode: ON (only accessible paths)`);
  }
  
  return { graph, nodeCoords };
}

/**
 * Find the closest node to a given coordinate
 * @param {Object} coordinate - { x, y } coordinate
 * @param {Array} nodes - Array of node objects
 * @returns {String} Node ID of the closest node
 */
export function findClosestNode(coordinate, nodes) {
  let closestNode = null;
  let minDistance = Infinity;
  
  nodes.forEach(node => {
    const nodeId = node?.properties?.id || node?.id;
    const coords = node?.geometry?.coordinates || [0, 0];
    
    const distance = Math.sqrt(
      Math.pow(coords[0] - coordinate.x, 2) +
      Math.pow(coords[1] - coordinate.y, 2)
    );
    
    if (distance < minDistance) {
      minDistance = distance;
      closestNode = nodeId;
    }
  });
  
  console.log(`📍 Closest node to [${coordinate.x}, ${coordinate.y}]: ${closestNode} (distance: ${minDistance.toFixed(1)})`);
  return closestNode;
}

/**
 * Dijkstra's algorithm to find shortest path
 * @param {Object} graph - Graph adjacency list
 * @param {String} startNodeId - Starting node ID
 * @param {String} endNodeId - Destination node ID
 * @returns {Array} Array of node IDs representing the path
 */
export function dijkstra(graph, startNodeId, endNodeId) {
  console.log(`🔍 Finding path from ${startNodeId} to ${endNodeId}...`);
  
  // Check if start and end nodes exist in graph
  if (!graph[startNodeId]) {
    console.error(`❌ Start node "${startNodeId}" not found in graph`);
    return [];
  }
  if (!graph[endNodeId]) {
    console.error(`❌ End node "${endNodeId}" not found in graph`);
    return [];
  }
  
  const distances = {}; // shortest distance from start to each node
  const previous = {}; // previous node in optimal path
  const unvisited = new Set(); // unvisited nodes
  
  // Initialize distances
  Object.keys(graph).forEach(nodeId => {
    distances[nodeId] = Infinity;
    previous[nodeId] = null;
    unvisited.add(nodeId);
  });
  distances[startNodeId] = 0;
  
  while (unvisited.size > 0) {
    // Find unvisited node with smallest distance
    let currentNode = null;
    let smallestDistance = Infinity;
    unvisited.forEach(nodeId => {
      if (distances[nodeId] < smallestDistance) {
        smallestDistance = distances[nodeId];
        currentNode = nodeId;
      }
    });
    
    // If we can't find a reachable node, path doesn't exist
    if (currentNode === null || smallestDistance === Infinity) {
      console.error(`❌ No path found from ${startNodeId} to ${endNodeId}`);
      return [];
    }
    
    // If we reached the destination, we're done
    if (currentNode === endNodeId) {
      break;
    }
    
    // Remove from unvisited
    unvisited.delete(currentNode);
    
    // Update distances to neighbors
    const neighbors = graph[currentNode] || [];
    neighbors.forEach(neighbor => {
      if (!unvisited.has(neighbor.to)) return;
      
      const newDistance = distances[currentNode] + neighbor.distance;
      if (newDistance < distances[neighbor.to]) {
        distances[neighbor.to] = newDistance;
        previous[neighbor.to] = currentNode;
      }
    });
  }
  
  // Reconstruct path
  const path = [];
  let currentNode = endNodeId;
  while (currentNode !== null) {
    path.unshift(currentNode);
    currentNode = previous[currentNode];
  }
  
  // If path doesn't start with startNodeId, no path exists
  if (path[0] !== startNodeId) {
    console.error(`❌ No path found from ${startNodeId} to ${endNodeId}`);
    return [];
  }
  
  console.log(`✅ Path found! ${path.length} nodes, distance: ${distances[endNodeId].toFixed(1)}`);
  console.log(`   Path: ${path.join(' → ')}`);
  
  return path;
}

/**
 * Find path between two coordinates
 * @param {Object} startCoord - Starting coordinate { x, y }
 * @param {Object} endCoord - End coordinate { x, y }
 * @param {Array} nodes - Array of node objects
 * @param {Array} edges - Array of edge objects
 * @param {Boolean} accessibleOnly - If true, only use accessible edges
 * @returns {Object} { path: Array of node IDs, coordinates: Array of [x, y] }
 */
export function findPath(startCoord, endCoord, nodes, edges, accessibleOnly = false) {
  console.log(`\n🗺️ === PATHFINDING START ===`);
  console.log(`   Start: [${startCoord.x}, ${startCoord.y}]`);
  console.log(`   End: [${endCoord.x}, ${endCoord.y}]`);
  console.log(`   Accessible Only: ${accessibleOnly}`);
  
  // Find closest nodes to start and end coordinates
  const startNodeId = findClosestNode(startCoord, nodes);
  const endNodeId = findClosestNode(endCoord, nodes);
  
  if (!startNodeId || !endNodeId) {
    console.error(`❌ Could not find nodes near coordinates`);
    return { path: [], coordinates: [] };
  }
  
  // Build graph
  const { graph, nodeCoords } = buildGraph(nodes, edges, accessibleOnly);
  
  // Find path using Dijkstra
  const path = dijkstra(graph, startNodeId, endNodeId);
  
  // Convert path to coordinates
  const coordinates = path.map(nodeId => nodeCoords[nodeId]);
  
  console.log(`🗺️ === PATHFINDING END ===\n`);
  
  return { path, coordinates, nodeCoords };
}

