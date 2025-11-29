// components/ui/LocationCard.tsx
// LocationCard component with new design + backend integration
import { Ionicons } from '@expo/vector-icons';
import React from 'react';
import { StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { categories } from '../../CategoryContext';

const COLORS = {
  maroon: '#8B0000',
  white: '#FFFFFF',
  lightGrey: '#F4F4F4', 
  grey: '#B0B0B0',
  dark: '#333333',
};

// Category configuration for icons and colors
const CATEGORY_CONFIG: { [key: string]: { icon: any; color: string } } = {
  office: { icon: 'briefcase-outline', color: '#2E7D32' },
  classroom: { icon: 'school-outline', color: '#e74c3c' },
  laboratory: { icon: 'flask-outline', color: '#D81B60' },
  amenity: { icon: 'restaurant-outline', color: '#F9A825' },
  library: { icon: 'library-outline', color: '#1976D2' },
  default: { icon: 'location-outline', color: '#95a5a6' },
};

interface LocationCardProps {
  node: any; // Backend node object
  onGetDirections?: (node: any) => void;
  onBookmark?: (node: any) => void;
  isBookmarked?: boolean;
}

export default function LocationCard({ 
  node, 
  onGetDirections, 
  onBookmark, 
  isBookmarked = false 
}: LocationCardProps) {
  // Extract node data from backend format
  const name = node?.properties?.name || node?.name || 'Unknown Location';
  const nodeId = node?.properties?.id || node?.id || 'unknown';
  const category = (node?.properties?.category || 'default').toLowerCase();
  const buildingName = node?.properties?.building_name || 'Unknown Building';
  const floor = node?.properties?.floor || 'Ground Floor';
  
  // Get category configuration
  const categoryInfo = categories.find(cat => cat.name.toLowerCase() === category);
  const iconColor = categoryInfo ? categoryInfo.color : COLORS.white;
  const categoryConfig = CATEGORY_CONFIG[category] || CATEGORY_CONFIG.default;
  
  // Format location details
  const locationDetails = `${buildingName}, ${floor}`;

  // Handle bookmark press
  const handleBookmarkPress = () => {
    if (onBookmark) {
      onBookmark(node);
    }
  };

  // Handle get directions press
  const handleGetDirections = () => {
    if (onGetDirections) {
      onGetDirections(node);
    }
  };

  return (
    <View style={[styles.card, { backgroundColor: COLORS.maroon }]}>
      
      <View style={styles.cardTopRow}>
        <View style={styles.cardTextContent}>
          <View style={{ flexDirection: 'row', alignItems: 'center' }}>
            <Text style={[styles.cardTitle, { color: COLORS.white }]}>{name}</Text>
            <Ionicons 
              name={categoryConfig.icon} 
              size={16} 
              color={iconColor}
              style={{ marginLeft: 8 }}
            />
          </View>
          <Text style={[styles.cardDetails, { color: COLORS.lightGrey }]}>{locationDetails}</Text>
        </View>

        {/* THE HEART BUTTON */}
        <TouchableOpacity 
          style={styles.heartButton}
          onPress={handleBookmarkPress}
        >
          <Ionicons 
            name={isBookmarked ? 'heart' : 'heart-outline'} 
            size={24} 
            color={COLORS.white} 
          />
        </TouchableOpacity>
      </View>

      {/* GET DIRECTIONS BUTTON */}
      <TouchableOpacity 
        style={[styles.directionsButton, { backgroundColor: COLORS.white }]}
        onPress={handleGetDirections}
      >
        <Ionicons name="navigate-outline" size={16} color={COLORS.maroon} />
        <Text style={styles.directionsText}>Get Directions</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 15,
    padding: 20,
    marginBottom: 15,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  cardTopRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 15, 
  },
  cardTextContent: {
    flex: 1, 
    paddingRight: 10, 
  },
  heartButton: {
    paddingLeft: 10, 
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    flexShrink: 1, 
  },
  cardDetails: {
    fontSize: 14,
    marginTop: 5,
  },
  directionsButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
    borderRadius: 25,
  },
  directionsText: {
    color: COLORS.maroon,
    marginLeft: 8,
    fontSize: 14,
    fontWeight: '600',
  },
});

