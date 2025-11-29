import React, { useEffect, useRef, useState } from "react";
import {
  Dimensions,
  Image,
  Platform,
  SafeAreaView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
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
import { Ionicons } from '@expo/vector-icons';

const { width: screenWidth, height: screenHeight } = Dimensions.get("window");
const IMAGE_WIDTH = 1449;
const IMAGE_HEIGHT = 2565;

// Calculate header height (approximate) - more accurate measurement
const HEADER_HEIGHT = Platform.OS === 'ios' ? 85 : 55; // Total header height including padding
const BOTTOM_BUTTON_HEIGHT = 100; // Approximate height of bottom button area with SafeAreaView
const VISIBLE_MAP_HEIGHT = screenHeight - HEADER_HEIGHT - BOTTOM_BUTTON_HEIGHT;

// Colors
const COLORS = {
  maroon: '#8B0000',
  white: '#FFFFFF',
  grey: '#B0B0B0',
  dark: '#333333',
};

export default function LocationPickerScreen({ onLocationSelected, onCancel, initialCoordinate }) {
  // Calculate initial scale to fit map on screen (less zoomed in)
  const initialScale = Math.min(
    screenWidth / IMAGE_WIDTH,
    screenHeight / IMAGE_HEIGHT
  ) * 0.6; // Changed from 0.9 to 0.6 for less zoom
  
  const scale = useSharedValue(initialScale);
  const translateX = useSharedValue((screenWidth - IMAGE_WIDTH * initialScale) / 2);
  const translateY = useSharedValue((screenHeight - IMAGE_HEIGHT * initialScale) / 2);
  
  const savedTranslateX = useSharedValue(0);
  const savedTranslateY = useSharedValue(0);
  const savedScale = useSharedValue(1);

  // Initialize with initial coordinate if provided
  useEffect(() => {
    if (initialCoordinate) {
      // Center the map on the initial coordinate with less zoom
      const targetScale = Math.min(
        screenWidth / IMAGE_WIDTH,
        screenHeight / IMAGE_HEIGHT
      ) * 0.7; // Less zoomed in (was 2.0)
      const centerX = screenWidth / 2;
      const centerY = screenHeight / 2;
      
      // Calculate translation to center the coordinate
      const targetTranslateX = centerX - (initialCoordinate.x * targetScale);
      const targetTranslateY = centerY - (initialCoordinate.y * targetScale);
      
      scale.value = withTiming(targetScale, { duration: 300 });
      translateX.value = withTiming(targetTranslateX, { duration: 300 });
      translateY.value = withTiming(targetTranslateY, { duration: 300 });
    }
  }, [initialCoordinate]);

  // Helper function to constrain translation within bounds
  const constrainTranslation = (transX, transY, currentScale) => {
    'worklet';
    const scaledImageWidth = IMAGE_WIDTH * currentScale;
    const scaledImageHeight = IMAGE_HEIGHT * currentScale;
    
    let constrainedX = transX;
    let constrainedY = transY;
    
    // X axis constraints
    if (scaledImageWidth <= screenWidth) {
      constrainedX = (screenWidth - scaledImageWidth) / 2;
    } else {
      const maxX = 0;
      const minX = screenWidth - scaledImageWidth;
      constrainedX = Math.max(minX, Math.min(maxX, transX));
    }
    
    // Y axis constraints
    if (scaledImageHeight <= screenHeight) {
      constrainedY = (screenHeight - scaledImageHeight) / 2;
    } else {
      const maxY = 0;
      const minY = screenHeight - scaledImageHeight;
      constrainedY = Math.max(minY, Math.min(maxY, transY));
    }
    
    return { x: constrainedX, y: constrainedY };
  };

  // Get current center point in map coordinates (worklet function)
  const getCenterMapCoordinate = () => {
    'worklet';
    const centerX = screenWidth / 2;
    const centerY = screenHeight / 2;
    
    // Convert screen center to map coordinates
    const mapX = (centerX - translateX.value) / scale.value;
    const mapY = (centerY - translateY.value) / scale.value;
    
    return { x: mapX, y: mapY };
  };

  // JS function to handle location selection
  const handleLocationSelectedJS = (coordinate) => {
    console.log('📍 Selected location:', coordinate);
    onLocationSelected(coordinate);
  };

  // Pan gesture
  const panGesture = Gesture.Pan()
    .onStart(() => {
      savedTranslateX.value = translateX.value;
      savedTranslateY.value = translateY.value;
    })
    .onUpdate((event) => {
      const newX = savedTranslateX.value + event.translationX;
      const newY = savedTranslateY.value + event.translationY;
      const constrained = constrainTranslation(newX, newY, scale.value);
      translateX.value = constrained.x;
      translateY.value = constrained.y;
    })
    .onEnd(() => {
      const constrained = constrainTranslation(translateX.value, translateY.value, scale.value);
      translateX.value = withTiming(constrained.x);
      translateY.value = withTiming(constrained.y);
    });

  // Pinch gesture
  const pinchGesture = Gesture.Pinch()
    .onStart(() => {
      savedScale.value = scale.value;
    })
    .onUpdate((event) => {
      const minScale = Math.min(screenWidth / IMAGE_WIDTH, screenHeight / IMAGE_HEIGHT) * 0.3; // Allow more zoom out
      const maxScale = 5;
      scale.value = Math.max(minScale, Math.min(event.scale * savedScale.value, maxScale));
    })
    .onEnd(() => {
      const minScale = Math.min(screenWidth / IMAGE_WIDTH, screenHeight / IMAGE_HEIGHT) * 0.3; // Allow more zoom out
      if (scale.value < minScale) {
        scale.value = withTiming(minScale);
      } else if (scale.value > 5) {
        scale.value = withTiming(5);
      }
      
      const constrained = constrainTranslation(translateX.value, translateY.value, scale.value);
      translateX.value = withTiming(constrained.x);
      translateY.value = withTiming(constrained.y);
    });

  const composedGesture = Gesture.Simultaneous(panGesture, pinchGesture);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: translateX.value },
      { translateY: translateY.value },
      { scale: scale.value },
    ],
  }));

  const handleEnterLocation = () => {
    // Get current animated values synchronously
    const currentTranslateX = translateX.value;
    const currentTranslateY = translateY.value;
    const currentScale = scale.value;
    
    // Calculate center point in map coordinates (pixel coordinates on the map image)
    // Use the actual pin position (center of visible map area, accounting for header)
    const centerX = screenWidth / 2;
    const centerY = HEADER_HEIGHT + (VISIBLE_MAP_HEIGHT / 2); // Center of visible map area
    
    // Convert screen coordinates to map pixel coordinates
    // Formula: mapCoord = (screenCoord - translation) / scale
    const mapX = (centerX - currentTranslateX) / currentScale;
    const mapY = (centerY - currentTranslateY) / currentScale;
    
    // Ensure coordinates are within map bounds
    const boundedX = Math.max(0, Math.min(IMAGE_WIDTH, mapX));
    const boundedY = Math.max(0, Math.min(IMAGE_HEIGHT, mapY));
    
    const coordinate = { x: boundedX, y: boundedY };
    
    console.log('📍 Location Picker - Coordinate Calculation:');
    console.log('   Screen center:', { x: centerX, y: centerY });
    console.log('   Map translation:', { x: currentTranslateX, y: currentTranslateY });
    console.log('   Map scale:', currentScale);
    console.log('   Calculated map coordinate (pixels):', coordinate);
    
    handleLocationSelectedJS(coordinate);
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={onCancel} style={styles.cancelButton}>
          <Ionicons name="arrow-back" size={24} color={COLORS.white} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Select Your Location</Text>
        <View style={styles.placeholder} />
      </View>

      {/* Map Container */}
      <View style={styles.mapContainer}>
        {/* Fixed Center Pin (Pirates Logo) - Must be BEFORE GestureDetector to be on top */}
        <View style={styles.centerPinContainer} pointerEvents="none">
          <Image
            source={require("../assets/pirate-logo.png")}
            style={styles.centerPin}
            resizeMode="contain"
          />
          <View style={styles.pinShadow} />
        </View>

        {/* Map with gestures - Pin stays fixed, only map moves */}
        <GestureDetector gesture={composedGesture}>
          <Animated.View style={[styles.mapWrapper, animatedStyle]}>
            <Image
              source={require("../assets/maps/map.png")}
              style={styles.mapImage}
            />
          </Animated.View>
        </GestureDetector>

        {/* Instructions */}
        <View style={styles.instructionsContainer}>
          <Text style={styles.instructionsText}>
            Drag the map to position the pin where you are
          </Text>
        </View>
      </View>

      {/* Bottom Button */}
      <SafeAreaView style={styles.bottomSafeArea}>
        <View style={styles.bottomContainer}>
          <TouchableOpacity
            style={styles.enterButton}
            onPress={handleEnterLocation}
            activeOpacity={0.8}
          >
            <Ionicons name="checkmark-circle" size={24} color={COLORS.white} />
            <Text style={styles.enterButtonText}>Enter Location</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.maroon,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: Platform.OS === 'ios' ? 50 : 20,
    paddingHorizontal: 20,
    paddingBottom: 15,
    backgroundColor: COLORS.maroon,
    zIndex: 100, // Header above map but below pin
  },
  cancelButton: {
    padding: 5,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.white,
  },
  placeholder: {
    width: 34, // Same width as cancel button for centering
  },
  mapContainer: {
    flex: 1,
    backgroundColor: COLORS.dark,
    position: 'relative',
    overflow: 'hidden',
  },
  mapWrapper: {
    width: IMAGE_WIDTH,
    height: IMAGE_HEIGHT,
    position: 'absolute',
    top: 0,
    left: 0,
  },
  mapImage: {
    width: IMAGE_WIDTH,
    height: IMAGE_HEIGHT,
    position: 'absolute',
    top: 0,
    left: 0,
  },
  centerPinContainer: {
    position: 'absolute',
    // Center of the mapContainer (which is flex: 1, so it takes remaining space)
    top: '50%',
    left: '50%',
    width: 60,
    height: 60,
    marginLeft: -30, // Half of width to center horizontally
    marginTop: -30,  // Half of height to center vertically
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
    pointerEvents: 'none', // Ensure pin doesn't intercept touches - map can move underneath
  },
  centerPin: {
    width: 60,
    height: 60,
    zIndex: 1001,
  },
  pinShadow: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: 'rgba(0, 0, 0, 0.3)',
    marginTop: -2,
    zIndex: 1000,
  },
  instructionsContainer: {
    position: 'absolute',
    top: 20,
    left: 0,
    right: 0,
    alignItems: 'center',
    zIndex: 999,
  },
  instructionsText: {
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    color: COLORS.white,
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    fontSize: 14,
    fontWeight: '500',
  },
  bottomSafeArea: {
    backgroundColor: COLORS.white,
    zIndex: 1000,
  },
  bottomContainer: {
    padding: 20,
    paddingTop: 15,
    paddingBottom: Platform.OS === 'ios' ? 10 : 15,
    backgroundColor: COLORS.white,
    borderTopLeftRadius: 30,
    borderTopRightRadius: 30,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.1,
    shadowRadius: 10,
    elevation: 10,
  },
  enterButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: COLORS.maroon,
    paddingVertical: 16,
    paddingHorizontal: 30,
    borderRadius: 25,
    gap: 10,
  },
  enterButtonText: {
    color: COLORS.white,
    fontSize: 18,
    fontWeight: '600',
  },
});

