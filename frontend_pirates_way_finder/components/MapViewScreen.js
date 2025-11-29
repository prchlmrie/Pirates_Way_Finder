import React from "react";
import { View } from "react-native";
import ZoomableMap from "./ZoomableMap";

export default function MapViewScreen({ selectedNode, startCoordinate }) {
  // No modal popup - just show the map with navigation
  // The ZoomableMap will handle focusing on the selected node
  
  return (
    <View style={{ flex: 1 }}>
      <ZoomableMap 
        focusNode={selectedNode} 
        startCoordinate={startCoordinate}
        onNodePress={() => {}} // Empty handler - no popup when tapping nodes
      />
    </View>
  );
}

// No styles needed - modal removed!

