import React, { useEffect, useRef, useState } from "react";
import { ActivityIndicator, Dimensions, Image, Platform, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import {
  Gesture,
  GestureDetector,
} from "react-native-gesture-handler";
import Animated, {
  runOnJS,
  useAnimatedStyle,
  useSharedValue,
  withTiming,
} from "react-native-reanimated";
import Svg, { Circle, Polyline, Path } from "react-native-svg";
import { Ionicons } from '@expo/vector-icons';
import { getNodes, getShortestPath, getWalkableGrid } from "../api/mapApi";
import DirectionsBottomSheet from "./DirectionsBottomSheet";

const { width: screenWidth, height: screenHeight } = Dimensions.get("window");
const IMAGE_WIDTH = 1449;  // Updated to match new resized map
const IMAGE_HEIGHT = 2565; // Updated to match new resized map

// Border settings
const BORDER_WIDTH = 0; // No border
const CONTAINER_WIDTH = IMAGE_WIDTH; // Total width without border
const CONTAINER_HEIGHT = IMAGE_HEIGHT; // Total height without border

// Marker configuration
const MARKER_CONFIG = {
  radius: 15,        // Scaled down from 40 to match smaller image
  fillColor: "#E74C3C",  // Bright red
  strokeColor: "#FFFFFF", // White border
  strokeWidth: 2,
  opacity: 0.9,
};

// Helper function to create smooth SVG path string using Catmull-Rom-like smoothing
const createSmoothPath = (coordinates) => {
  if (!coordinates || coordinates.length === 0) return '';
  if (coordinates.length === 1) {
    return `M ${coordinates[0].x} ${coordinates[0].y}`;
  }
  
  if (coordinates.length === 2) {
    // Simple line for 2 points
    return `M ${coordinates[0].x} ${coordinates[0].y} L ${coordinates[1].x} ${coordinates[1].y}`;
  }
  
  // For 3+ points, use smooth curves
  let path = `M ${coordinates[0].x} ${coordinates[0].y}`;
  
  // Use quadratic bezier curves for smooth transitions
  for (let i = 1; i < coordinates.length; i++) {
    const prev = coordinates[i - 1];
    const curr = coordinates[i];
    
    if (i === 1) {
      // First segment: line to second point
      path += ` L ${curr.x} ${curr.y}`;
    } else if (i === coordinates.length - 1) {
      // Last segment: smooth curve to end
      const prevPrev = coordinates[i - 2];
      // Control point is between previous two points for smooth transition
      const controlX = prev.x + (curr.x - prevPrev.x) * 0.3;
      const controlY = prev.y + (curr.y - prevPrev.y) * 0.3;
      path += ` Q ${controlX} ${controlY} ${curr.x} ${curr.y}`;
    } else {
      // Middle segments: smooth curves
      const prevPrev = coordinates[i - 2];
      const next = coordinates[i + 1];
      
      // Calculate control point for smooth curve
      const controlX = prev.x + (curr.x - prevPrev.x) * 0.2;
      const controlY = prev.y + (curr.y - prevPrev.y) * 0.2;
      
      // Use quadratic bezier curve
      path += ` Q ${controlX} ${controlY} ${curr.x} ${curr.y}`;
    }
  }
  
  return path;
};

export default function ZoomableMap({ onNodePress, focusNode, startCoordinate }) {
  const [nodes, setNodes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [highlightedNodeId, setHighlightedNodeId] = useState(null);
  const [pathCoordinates, setPathCoordinates] = useState([]);
  const [calculatingPath, setCalculatingPath] = useState(false);
  const [walkablePaths, setWalkablePaths] = useState([]);
  const [showWalkablePaths, setShowWalkablePaths] = useState(false); // Hidden by default for better performance
  const [accessibilityMode, setAccessibilityMode] = useState(false);
  const [instructions, setInstructions] = useState([]);
  const [distance, setDistance] = useState(0);
  const [time, setTime] = useState(0);
  const [showDirections, setShowDirections] = useState(false);

  // Calculate initial scale to fit container (map + border) on screen
  const initialScale = Math.min(
    screenWidth / CONTAINER_WIDTH,
    screenHeight / CONTAINER_HEIGHT
  ) * 0.95; // 0.95 for a bit of padding
  
  const scale = useSharedValue(initialScale);
  const translateX = useSharedValue((screenWidth - CONTAINER_WIDTH * initialScale) / 2);
  const translateY = useSharedValue((screenHeight - CONTAINER_HEIGHT * initialScale) / 2);
  const focalX = useSharedValue(0);
  const focalY = useSharedValue(0);
  
  // Track pan gesture state for tap detection
  const panStartTime = useSharedValue(0);
  const panStartX = useSharedValue(0);
  const panStartY = useSharedValue(0);
  const savedTranslateX = useSharedValue(0);
  const savedTranslateY = useSharedValue(0);
  const savedScale = useSharedValue(1);

  // Mouse drag state
  const containerRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const mouseStartPos = useRef({ x: 0, y: 0 });
  const lastTranslate = useRef({ x: 0, y: 0 });

  useEffect(() => {
    (async () => {
      try {
        console.log('🔄 Fetching nodes and walkable paths from backend...');
        const [nodesData, walkableData] = await Promise.all([
          getNodes(),
          getWalkableGrid()
        ]);
        
        console.log(`✅ Fetched ${nodesData.length} nodes`);
        console.log(`✅ Fetched ${walkableData.length} walkable cells`);
        
        if (nodesData.length > 0) {
          console.log('Sample node:', JSON.stringify(nodesData[0], null, 2));
        }
        
        setNodes(nodesData);
        setWalkablePaths(walkableData);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // Focus on the selected node when it changes OR accessibility mode changes
  useEffect(() => {
    if (focusNode && startCoordinate && nodes.length > 0) {
      console.log('📍 Triggering navigation to node:', focusNode?.properties?.name);
      focusOnNode(focusNode);
      calculatePath(startCoordinate, focusNode);
    } else if (focusNode && startCoordinate) {
      console.log('⚠️ Waiting for nodes... loaded:', nodes.length);
    }
  }, [focusNode, nodes.length, accessibilityMode]); // Recalculate when accessibility mode changes

  // Function to calculate path between start and destination using grid-based pathfinding
  const calculatePath = async (start, destination) => {
    console.log('\n🗺️ === GRID-BASED PATH CALCULATION ===');
    console.log('Start:', start);
    console.log('Destination:', destination?.properties?.name || destination);
    
    if (!start || !destination) {
      console.error('❌ Missing start or destination');
      return;
    }

    const [destX, destY] = getNodeCoordinates(destination);
    
    console.log(`📍 Calculating path from [${start.x}, ${start.y}] to [${destX}, ${destY}]`);
    
    try {
      setCalculatingPath(true);
      
      // Call the grid-based pathfinding API with accessibility mode
      const response = await getShortestPath(start.x, start.y, destX, destY, accessibilityMode);
      
      console.log('📦 Backend response:', response);
      
      if (response && response.path && response.path.length > 0) {
        // Convert the path data to coordinate format for Polyline
        const coordinates = response.path.map(point => ({ x: point.x, y: point.y }));
        setPathCoordinates(coordinates);
        
        // Set instructions, distance, and time
        setInstructions(response.instructions || []);
        setDistance(response.distance_meters || 0);
        setTime(response.estimated_time_minutes || 0);
        
        console.log(`✅ PATH SET! ${coordinates.length} waypoints`);
        console.log(`📝 Instructions: ${response.instructions?.length || 0} steps`);
        console.log(`♿ Accessibility mode was: ${accessibilityMode ? 'ON (avoiding stairs)' : 'OFF'}`);
        console.log('   First 3 points:', coordinates.slice(0, 3));
        console.log('   Last 3 points:', coordinates.slice(-3));
        console.log('🟢 GREEN LINE SHOULD BE VISIBLE NOW!');
      } else {
        setPathCoordinates([]);
        setInstructions([]);
        setDistance(0);
        setTime(0);
        console.error(`❌ NO PATH FOUND!`);
        console.error('   Backend returned empty or null path');
        const message = accessibilityMode 
          ? 'No accessible path found! Try turning off accessibility mode or check if ramps are available.'
          : 'No path found! This location may not be reachable from your starting point.';
        alert(message);
      }
    } catch (error) {
      console.error('❌ Error calculating path:', error);
      setPathCoordinates([]);
      setInstructions([]);
      setDistance(0);
      setTime(0);
      alert('Error calculating path. Please try again.');
    } finally {
      setCalculatingPath(false);
    }
  };

  // Function to focus and zoom to a specific node
  const focusOnNode = (node) => {
    const [nodeX, nodeY] = getNodeCoordinates(node);
    const nodeId = node?.properties?.id || node?.id;
    
    console.log(`🎯 Focusing on node: ${nodeId} at [${nodeX}, ${nodeY}]`);
    
    // Set this node as highlighted
    setHighlightedNodeId(nodeId);
    
    // Calculate the position to center the node on screen (accounting for border)
    const containerLeft = screenWidth / 2 - CONTAINER_WIDTH / 2;
    const containerTop = screenHeight / 2 - CONTAINER_HEIGHT / 2;
    
    // Zoom level for focused node
    const targetScale = 2.5;
    
    // Node coordinates in container space (no border offset)
    const nodeXWithBorder = nodeX;
    const nodeYWithBorder = nodeY;
    
    // Calculate translation to center the node
    const targetTranslateX = screenWidth / 2 - (nodeXWithBorder * targetScale) - containerLeft * targetScale;
    const targetTranslateY = screenHeight / 2 - (nodeYWithBorder * targetScale) - containerTop * targetScale;
    
    // Animate to the target position
    scale.value = withTiming(targetScale, { duration: 500 });
    translateX.value = withTiming(targetTranslateX, { duration: 500 });
    translateY.value = withTiming(targetTranslateY, { duration: 500 });
    
    // KEEP destination highlighted - don't fade away!
    // User needs to see where they're going
  };

  // Note: Accessibility mode can be added later by implementing
  // grid-based filtering in the backend (e.g., marking ramps vs stairs)

  // Helper to get coordinates from a node (supports multiple formats)
  const getNodeCoordinates = (node) => {
    if (node?.geometry?.coordinates) {
      return node.geometry.coordinates; // [x, y] format
    } else if (node?.x !== undefined && node?.y !== undefined) {
      return [node.x, node.y]; // {x, y} format
    }
    return [0, 0]; // fallback
  };

  // Handle node tap detection (runs on JS thread)
  const handleTapDetection = (eventX, eventY, scaleVal, transX, transY) => {
    if (!onNodePress || nodes.length === 0) return;
    
    // Map container's initial top-left position (before transforms) - no border
    const containerLeft = screenWidth / 2 - CONTAINER_WIDTH / 2;
    const containerTop = screenHeight / 2 - CONTAINER_HEIGHT / 2;
    
    // Convert screen coordinates to container coordinates (no border)
    // The transform applies: scale first, then translate (in CSS transform order)
    // So we need to: subtract container position, subtract translation, then divide by scale
    const containerX = (eventX - containerLeft - transX) / scaleVal;
    const containerY = (eventY - containerTop - transY) / scaleVal;
    
    // Convert to image coordinates (no border offset)
    const imageX = containerX;
    const imageY = containerY;
    
    // Find nearest node within threshold (scaled by current zoom level)
    // Use a threshold relative to marker size (about 2.5x the marker radius)
    const threshold = (MARKER_CONFIG.radius * 2.5) / scaleVal; // Threshold scales with zoom
    let nearestNode = null;
    let minDistance = Infinity;
    
    nodes.forEach((node) => {
      const [nodeX, nodeY] = getNodeCoordinates(node);
      const distance = Math.sqrt((imageX - nodeX) ** 2 + (imageY - nodeY) ** 2);
      if (distance < threshold && distance < minDistance) {
        minDistance = distance;
        nearestNode = node;
      }
    });
    
    if (nearestNode) {
      onNodePress(nearestNode);
    }
  };

  // Helper function to constrain translation within bounds (no border)
  const constrainTranslation = (transX, transY, currentScale) => {
    'worklet';
    const scaledContainerWidth = CONTAINER_WIDTH * currentScale;
    const scaledContainerHeight = CONTAINER_HEIGHT * currentScale;
    
    let constrainedX = transX;
    let constrainedY = transY;
    
    // X axis constraints - constrain to container (no border)
    if (scaledContainerWidth <= screenWidth) {
      // Center if smaller than screen
      constrainedX = (screenWidth - scaledContainerWidth) / 2;
    } else {
      // Constrain to prevent panning beyond edges
      const maxX = 0; // Right edge at screen right
      const minX = screenWidth - scaledContainerWidth; // Left edge at screen left
      constrainedX = Math.max(minX, Math.min(maxX, transX));
    }
    
    // Y axis constraints - constrain to container (no border)
    if (scaledContainerHeight <= screenHeight) {
      // Center if smaller than screen
      constrainedY = (screenHeight - scaledContainerHeight) / 2;
    } else {
      // Constrain to prevent panning beyond edges
      const maxY = 0; // Top edge at screen top
      const minY = screenHeight - scaledContainerHeight; // Bottom edge at screen bottom
      constrainedY = Math.max(minY, Math.min(maxY, transY));
    }
    
    return { x: constrainedX, y: constrainedY };
  };

  // Pan gesture using new Gesture API
  const panGesture = Gesture.Pan()
    .onStart(() => {
      savedTranslateX.value = translateX.value;
      savedTranslateY.value = translateY.value;
      panStartTime.value = Date.now();
      panStartX.value = translateX.value;
      panStartY.value = translateY.value;
    })
    .onUpdate((event) => {
      const newX = savedTranslateX.value + event.translationX;
      const newY = savedTranslateY.value + event.translationY;
      const constrained = constrainTranslation(newX, newY, scale.value);
      translateX.value = constrained.x;
      translateY.value = constrained.y;
    })
    .onEnd((event) => {
      // Check if this was a tap (quick, small movement)
      const duration = Date.now() - panStartTime.value;
      const distance = Math.sqrt(
        event.translationX ** 2 + event.translationY ** 2
      );
      
      if (duration < 200 && distance < 10) {
        // This was a tap - detect if it hit a node
        runOnJS(handleTapDetection)(
          event.x,
          event.y,
          scale.value,
          translateX.value,
          translateY.value
        );
      }
      
      // Apply bounds constraint after pan ends
      const constrained = constrainTranslation(translateX.value, translateY.value, scale.value);
      translateX.value = withTiming(constrained.x);
      translateY.value = withTiming(constrained.y);
    });

  // Pinch gesture using new Gesture API
  const pinchGesture = Gesture.Pinch()
    .onStart(() => {
      savedScale.value = scale.value;
    })
    .onUpdate((event) => {
      // Allow zooming from fit-to-screen up to 3x (based on container without border)
      const minScale = Math.min(screenWidth / CONTAINER_WIDTH, screenHeight / CONTAINER_HEIGHT) * 0.9;
      const maxScale = 3;
      scale.value = Math.max(minScale, Math.min(event.scale * savedScale.value, maxScale));
    })
    .onEnd(() => {
      // Smooth reset to bounds (based on container without border)
      const minScale = Math.min(screenWidth / CONTAINER_WIDTH, screenHeight / CONTAINER_HEIGHT) * 0.9;
      if (scale.value < minScale) {
        scale.value = withTiming(minScale);
      } else if (scale.value > 3) {
        scale.value = withTiming(3);
      }
      
      // Apply bounds constraint after zoom ends
      const constrained = constrainTranslation(translateX.value, translateY.value, scale.value);
      translateX.value = withTiming(constrained.x);
      translateY.value = withTiming(constrained.y);
    });

  // Compose gestures to allow simultaneous pan and pinch
  const composedGesture = Gesture.Simultaneous(panGesture, pinchGesture);

  // Mouse wheel zoom handler (for web/desktop)
  const handleWheel = (event) => {
    if (Platform.OS !== 'web') return;
    
    event.preventDefault();
    const delta = -event.deltaY;
    const zoomIntensity = 0.001;
    
    // Calculate min scale to fit container (without border) on screen
    const minScale = Math.min(screenWidth / CONTAINER_WIDTH, screenHeight / CONTAINER_HEIGHT) * 0.9;
    const maxScale = 3;
    
    let newScale = scale.value + delta * zoomIntensity;
    
    // Clamp scale to fit-to-screen minimum and max zoom
    newScale = Math.max(minScale, Math.min(newScale, maxScale));
    
    // Get mouse position relative to the container
    const rect = event.currentTarget.getBoundingClientRect();
    const mouseX = event.clientX - rect.left;
    const mouseY = event.clientY - rect.top;
    
    // Zoom towards mouse cursor
    const scaleChange = newScale / scale.value;
    const newTranslateX = mouseX - (mouseX - translateX.value) * scaleChange;
    const newTranslateY = mouseY - (mouseY - translateY.value) * scaleChange;
    
    // Apply bounds constraint (for container without border)
    const scaledContainerWidth = CONTAINER_WIDTH * newScale;
    const scaledContainerHeight = CONTAINER_HEIGHT * newScale;
    
    const maxTranslateX = 0;
    const minTranslateX = screenWidth - scaledContainerWidth;
    const maxTranslateY = 0;
    const minTranslateY = screenHeight - scaledContainerHeight;
    
    // Constrain X
    let constrainedX = newTranslateX;
    if (scaledContainerWidth <= screenWidth) {
      constrainedX = (screenWidth - scaledContainerWidth) / 2;
    } else {
      constrainedX = Math.min(maxTranslateX, Math.max(minTranslateX, newTranslateX));
    }
    
    // Constrain Y
    let constrainedY = newTranslateY;
    if (scaledContainerHeight <= screenHeight) {
      constrainedY = (screenHeight - scaledContainerHeight) / 2;
    } else {
      constrainedY = Math.min(maxTranslateY, Math.max(minTranslateY, newTranslateY));
    }
    
    translateX.value = constrainedX;
    translateY.value = constrainedY;
    scale.value = newScale;
  };

  // Mouse down handler
  const handleMouseDown = (event) => {
    if (Platform.OS !== 'web') return;
    
    setIsDragging(true);
    mouseStartPos.current = { x: event.clientX, y: event.clientY };
    lastTranslate.current = { x: translateX.value, y: translateY.value };
    event.preventDefault();
  };

  // Mouse move handler
  const handleMouseMove = (event) => {
    if (Platform.OS !== 'web' || !isDragging) return;
    
    const deltaX = event.clientX - mouseStartPos.current.x;
    const deltaY = event.clientY - mouseStartPos.current.y;
    
    const newX = lastTranslate.current.x + deltaX;
    const newY = lastTranslate.current.y + deltaY;
    
    // Apply bounds constraint (for container without border)
    const scaledContainerWidth = CONTAINER_WIDTH * scale.value;
    const scaledContainerHeight = CONTAINER_HEIGHT * scale.value;
    
    const maxTranslateX = 0;
    const minTranslateX = screenWidth - scaledContainerWidth;
    const maxTranslateY = 0;
    const minTranslateY = screenHeight - scaledContainerHeight;
    
    // Constrain X
    let constrainedX = newX;
    if (scaledContainerWidth <= screenWidth) {
      constrainedX = (screenWidth - scaledContainerWidth) / 2;
    } else {
      constrainedX = Math.min(maxTranslateX, Math.max(minTranslateX, newX));
    }
    
    // Constrain Y
    let constrainedY = newY;
    if (scaledContainerHeight <= screenHeight) {
      constrainedY = (screenHeight - scaledContainerHeight) / 2;
    } else {
      constrainedY = Math.min(maxTranslateY, Math.max(minTranslateY, newY));
    }
    
    translateX.value = constrainedX;
    translateY.value = constrainedY;
  };

  // Mouse up handler
  const handleMouseUp = (event) => {
    if (Platform.OS !== 'web') return;
    
    if (isDragging) {
      const deltaX = event.clientX - mouseStartPos.current.x;
      const deltaY = event.clientY - mouseStartPos.current.y;
      const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
      
      // If movement was minimal, treat it as a click
      if (distance < 5) {
        const rect = event.currentTarget.getBoundingClientRect();
        const clickX = event.clientX - rect.left;
        const clickY = event.clientY - rect.top;
        handleTapDetection(clickX, clickY, scale.value, translateX.value, translateY.value);
      }
    }
    
    setIsDragging(false);
  };

  // Add global mouse up listener to handle mouse up outside the container
  useEffect(() => {
    if (Platform.OS !== 'web') return;
    
    const handleGlobalMouseUp = () => {
      setIsDragging(false);
    };
    
    window.addEventListener('mouseup', handleGlobalMouseUp);
    return () => window.removeEventListener('mouseup', handleGlobalMouseUp);
  }, []);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: translateX.value },
      { translateY: translateY.value },
      { scale: scale.value },
    ],
  }));

  if (loading) {
    return (
      <View style={styles.loaderContainer}>
        <ActivityIndicator size="large" color="#333" />
      </View>
    );
  }

  return (
    <Animated.View 
      style={{ flex: 1, overflow: 'hidden' }}
      onWheel={Platform.OS === 'web' ? handleWheel : undefined}
      onMouseDown={Platform.OS === 'web' ? handleMouseDown : undefined}
      onMouseMove={Platform.OS === 'web' ? handleMouseMove : undefined}
      onMouseUp={Platform.OS === 'web' ? handleMouseUp : undefined}
      ref={containerRef}
    >

      {/* Calculating path indicator */}
      {calculatingPath && (
        <View style={styles.calculatingIndicator}>
          <ActivityIndicator size="small" color="#FFD700" />
          <Text style={styles.calculatingText}>Calculating path...</Text>
        </View>
      )}

      {/* Left Side Button Row - Accessibility and Turn-by-Turn */}
      <View style={styles.leftButtonRow}>
        {/* Accessibility Toggle Button */}
        <TouchableOpacity 
          style={[
            styles.leftButton,
            accessibilityMode && styles.accessibilityButtonActive
          ]}
          onPress={() => setAccessibilityMode(!accessibilityMode)}
          activeOpacity={0.8}
        >
          <Ionicons 
            name="accessibility-outline" 
            size={20} 
            color={accessibilityMode ? '#FFFFFF' : '#4CAF50'} 
          />
          <Text style={[
            styles.leftButtonText,
            accessibilityMode && styles.accessibilityTextActive
          ]}>
            {accessibilityMode ? 'Ramps ON' : 'Ramps OFF'}
          </Text>
        </TouchableOpacity>

        {/* Turn-by-Turn Directions Button */}
        {instructions.length > 0 && (
          <TouchableOpacity 
            style={[
              styles.leftButton,
              styles.directionsButton,
              showDirections && styles.directionsButtonActive
            ]}
            onPress={() => setShowDirections(!showDirections)}
            activeOpacity={0.8}
          >
            <Ionicons 
              name="navigate" 
              size={20} 
              color={showDirections ? '#FFFFFF' : '#0066CC'} 
            />
            <Text style={[
              styles.directionsButtonText,
              showDirections && styles.directionsButtonTextActive
            ]}>
              Directions
            </Text>
          </TouchableOpacity>
        )}
      </View>
      <GestureDetector gesture={composedGesture}>
        <Animated.View 
          style={[
            styles.mapContainer, 
            animatedStyle,
            isDragging && Platform.OS === 'web' ? { cursor: 'grabbing' } : { cursor: 'grab' }
          ]}
        >
            {/* Map image - no border offset - Animated.Image to work with transforms */}
            <Animated.Image
              source={require("../assets/maps/map.png")}
              style={[
                styles.mapImage, 
                {
                  width: IMAGE_WIDTH, 
                  height: IMAGE_HEIGHT,
                  left: 0,
                  top: 0,
                }
              ]}
            />

          <Svg
            style={[StyleSheet.absoluteFill, { zIndex: 10 }]}
            width={CONTAINER_WIDTH}
            height={CONTAINER_HEIGHT}
            viewBox={`0 0 ${CONTAINER_WIDTH} ${CONTAINER_HEIGHT}`}
            pointerEvents="none"
          >
            {/* Starting coordinate marker (if provided) - no border offset */}
            {startCoordinate && (
              <>
                <Circle
                  cx={startCoordinate.x}
                  cy={startCoordinate.y}
                  r={MARKER_CONFIG.radius + 5}
                  fill="none"
                  stroke="#4CAF50"
                  strokeWidth={3}
                  opacity={0.6}
                />
                <Circle
                  cx={startCoordinate.x}
                  cy={startCoordinate.y}
                  r={MARKER_CONFIG.radius}
                  fill="#4CAF50"
                  stroke="#FFFFFF"
                  strokeWidth={2}
                  opacity={1}
                />
              </>
            )}
            
            {/* Path coordinates - no border offset - SMOOTH CURVES */}
            {pathCoordinates.length > 0 ? (
              <>
                {/* Outer glow/shadow for the path */}
                <Path
                  d={createSmoothPath(pathCoordinates)}
                  fill="none"
                  stroke="rgba(76, 175, 80, 0.3)"
                  strokeWidth={12}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                {/* Main path line - GREEN for navigation - SMOOTH */}
                <Path
                  d={createSmoothPath(pathCoordinates)}
                  fill="none"
                  stroke="#4CAF50"
                  strokeWidth={6}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </>
            ) : null}

            {/* Walkable paths - no border offset */}
            {showWalkablePaths && walkablePaths
              .filter((cell, index) => index % 3 === 0)
              .map((cell, index) => (
                <Circle
                  key={`walkable-${index}`}
                  cx={cell.x}
                  cy={cell.y}
                  r={2.5}
                  fill="#0066CC"
                  opacity={0.4}
                />
              ))}

            {/* ONLY show the destination/highlighted node (cleaner map) - no border offset */}
            {highlightedNodeId && nodes.length > 0 && (() => {
              const highlightedNode = nodes.find(node => {
                const nodeId = node?.properties?.id || node?.id;
                return nodeId === highlightedNodeId;
              });
              
              if (!highlightedNode) return null;
              
              const [x, y] = getNodeCoordinates(highlightedNode);
              const offsetX = x;
              const offsetY = y;
              
              return (
                <React.Fragment key={`highlighted-${highlightedNodeId}`}>
                  {/* Pulsing rings for destination - FULL OPACITY so it doesn't fade */}
                  <Circle
                    cx={offsetX}
                    cy={offsetY}
                    r={MARKER_CONFIG.radius + 15}
                    fill="none"
                    stroke="#FFD700"
                    strokeWidth={3}
                    opacity={1}
                  />
                  <Circle
                    cx={offsetX}
                    cy={offsetY}
                    r={MARKER_CONFIG.radius + 10}
                    fill="none"
                    stroke="#FFD700"
                    strokeWidth={2}
                    opacity={1}
                  />
                  
                  {/* The destination marker */}
                  <Circle
                    cx={offsetX}
                    cy={offsetY}
                    r={MARKER_CONFIG.radius + 3}
                    fill="#FFD700"
                    stroke={MARKER_CONFIG.strokeColor}
                    strokeWidth={3}
                    opacity={1}
                  />
                </React.Fragment>
              );
            })()}
          </Svg>
          </Animated.View>
        </GestureDetector>
        
        {/* Directions Bottom Sheet */}
        <DirectionsBottomSheet
          instructions={instructions}
          distance={distance}
          time={time}
          visible={showDirections && instructions.length > 0}
          onClose={() => setShowDirections(false)}
        />
      </Animated.View>
  );
}

const styles = StyleSheet.create({
  mapContainer: {
    width: CONTAINER_WIDTH,  // No border
    height: CONTAINER_HEIGHT, // No border
    position: 'absolute',
    // Position at origin - transforms will handle positioning
    left: 0,
    top: 0,
    backgroundColor: 'transparent', // No red background
  },
  mapImage: {
    position: "absolute",
    width: IMAGE_WIDTH,
    height: IMAGE_HEIGHT,
  },
  loaderContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  debugOverlay: {
    position: 'absolute',
    top: 10,
    left: 10,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    padding: 10,
    borderRadius: 5,
    zIndex: 1000,
  },
  debugText: {
    color: 'white',
    fontSize: 12,
    fontFamily: Platform.OS === 'web' ? 'monospace' : 'Courier',
  },
  calculatingIndicator: {
    position: 'absolute',
    top: 70,
    left: 10,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 20,
    zIndex: 1000,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  calculatingText: {
    color: '#FFD700',
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 10,
  },
  leftButtonRow: {
    position: 'absolute',
    top: 10,
    left: 10,
    zIndex: 1000,
    flexDirection: 'column',
    gap: 10,
  },
  leftButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 20,
    borderWidth: 2,
    borderColor: '#4CAF50',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  directionsButton: {
    borderColor: '#0066CC',
  },
  leftButtonText: {
    marginLeft: 8,
    fontSize: 13,
    fontWeight: '600',
    color: '#4CAF50',
  },
  accessibilityButtonActive: {
    backgroundColor: '#4CAF50',
    borderColor: '#4CAF50',
  },
  accessibilityTextActive: {
    color: '#FFFFFF',
  },
  directionsButtonText: {
    marginLeft: 8,
    fontSize: 13,
    fontWeight: '600',
    color: '#0066CC',
  },
  directionsButtonActive: {
    backgroundColor: '#0066CC',
    borderColor: '#0066CC',
  },
  directionsButtonTextActive: {
    color: '#FFFFFF',
  },
});

