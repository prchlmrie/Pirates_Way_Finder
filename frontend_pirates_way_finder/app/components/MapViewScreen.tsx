import React from "react";
import { View } from "react-native";
import ZoomableMap from "../../components/ZoomableMap";

interface MapViewScreenProps {
  selectedNode?: any;
  startCoordinate?: { x: number; y: number };
}

export default function MapViewScreen({ selectedNode: externalSelectedNode, startCoordinate }: MapViewScreenProps) {
  return (
    <View style={{ flex: 1 }}>
      <ZoomableMap 
        onNodePress={() => {}} 
        focusNode={externalSelectedNode}
        startCoordinate={startCoordinate}
      />
    </View>
  );
}
