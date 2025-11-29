// app/(tabs)/home.tsx
import { Ionicons } from '@expo/vector-icons';
import { Stack, useRouter } from 'expo-router';
import React, { useEffect, useState } from 'react';
import { ActivityIndicator, Image, ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';
import MapViewScreen from '../components/MapViewScreen';
import LocationCard from '../../components/ui/LocationCard';
import LocationPickerScreen from '../../components/LocationPickerScreen';
import { getNodes } from '../../api/mapApi';
import { useBookmarks } from '../../contexts/BookmarkContext';
import { useCategory } from '../../CategoryContext';

// --- Define Colors ---
const COLORS = {
  maroon: '#8B0000',
  white: '#FFFFFF',
  lightGrey: '#F4F4F4',
  grey: '#B0B0B0',
  dark: '#333333',
  pink: '#FFE5E5',
};

// --- Custom Header Component ---
function HeaderTitle() {
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center' }}>
      <Image
        source={require('../../assets/pirate-logo.png')} 
        style={{ width: 40, height: 40, marginRight: 10 }}
        resizeMode="contain"
      />
      <Text style={styles.headerTitleText}>Pirates Way Finder</Text>
    </View>
  );
}

// Default starting coordinate (for pathfinding before GPS is available)
// Starting point at (671, 2453) - main entrance area
const DEFAULT_START_COORDINATE = { x: 671, y: 2453 };

// --- Main Home Screen Component ---
export default function HomeScreen() {
  const router = useRouter();
  const { isBookmarked, toggleBookmark } = useBookmarks();
  const { selectedCategory, setSelectedCategory, setIsMapViewActive } = useCategory();
  const [viewMode, setViewMode] = useState('List');
  const [nodes, setNodes] = useState([]);
  const [filteredNodes, setFilteredNodes] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);
  const [showLocationPicker, setShowLocationPicker] = useState(false);
  const [startCoordinate, setStartCoordinate] = useState(DEFAULT_START_COORDINATE);
  
  // Hide tab bar when location picker is open
  useEffect(() => {
    setIsMapViewActive(showLocationPicker || viewMode === 'Map');
  }, [showLocationPicker, viewMode, setIsMapViewActive]);
  
  // Fetch nodes from API on component mount
  useEffect(() => {
    fetchNodesData();
  }, []);

  // This is now handled in the combined useEffect above

  // Filter nodes whenever search query OR selected category changes
  useEffect(() => {
    filterNodes();
  }, [searchQuery, nodes, selectedCategory]);

  const fetchNodesData = async () => {
    try {
      setLoading(true);
      const data = await getNodes();
      
      // Filter to only show nodes with relevant categories
      const relevantNodes = data.filter(node => {
        const category = node?.properties?.category?.toLowerCase();
        return ['office', 'classroom', 'laboratory', 'amenity', 'library'].includes(category);
      });
      
      setNodes(relevantNodes);
      setFilteredNodes(relevantNodes);
      console.log(`✅ Loaded ${relevantNodes.length} locations`);
    } catch (error) {
      console.error('❌ Error fetching nodes:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterNodes = () => {
    let filtered = nodes;
    
    // First, filter by category if one is selected
    if (selectedCategory && selectedCategory !== 'all') {
      filtered = filtered.filter(node => {
        const nodeCategory = node?.properties?.category?.toLowerCase() || '';
        return nodeCategory === selectedCategory.toLowerCase();
      });
    }
    
    // Then, filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(node => {
        const name = node?.properties?.name?.toLowerCase() || '';
        const id = node?.properties?.id?.toLowerCase() || '';
        const category = node?.properties?.category?.toLowerCase() || '';
        const buildingName = node?.properties?.building_name?.toLowerCase() || '';
        const tags = node?.properties?.tags || [];
        
        // Search in name, id, category, building name, and tags
        return (
          name.includes(query) ||
          id.includes(query) ||
          category.includes(query) ||
          buildingName.includes(query) ||
          tags.some(tag => tag.toLowerCase().includes(query))
        );
      });
    }

    // Sort alphabetically by name
    filtered.sort((a, b) => {
      const nameA = (a?.properties?.name || a?.name || '').toLowerCase();
      const nameB = (b?.properties?.name || b?.name || '').toLowerCase();
      return nameA.localeCompare(nameB);
    });

    setFilteredNodes(filtered);
    console.log(`🔍 Filter - Category: ${selectedCategory || 'all'}, Search: "${searchQuery}", Results: ${filtered.length}`);
  };

  const handleGetDirections = (node) => {
    console.log('🧭 Getting directions to:', node?.properties?.name);
    setSelectedNode(node);
    setViewMode('Map');
  };

  const handleBookmark = (node) => {
    toggleBookmark(node);
  };

  const handleLocationSelected = (coordinate) => {
    console.log('✅ Location selected and saved:', coordinate);
    console.log('   Coordinate type: pixel coordinates on map.png');
    console.log('   This will be used as the starting point for pathfinding');
    setStartCoordinate(coordinate);
    setShowLocationPicker(false);
    // Optionally switch to map view to show the new starting point
    // setViewMode('Map');
  };

  const handleCancelLocationPicker = () => {
    setShowLocationPicker(false);
  };

  return (
    <View style={styles.container}>
      <Stack.Screen
        options={{
          headerShown: true,
          headerStyle: { backgroundColor: COLORS.maroon },
          headerTitle: () => <HeaderTitle />,
          headerTitleAlign: 'center',
          // Admin login removed - will be web-based
          headerRight: () => (
            <TouchableOpacity
              onPress={() => alert('About/Info page pressed!')}
              style={{ marginRight: 15 }}
            >
              <Ionicons name="information-circle-outline" size={30} color={COLORS.white} />
            </TouchableOpacity>
          ),
        }}
      />

      {/* Main Content Area */}
      <View style={styles.mainContent}>
        {/* Search Bar */}
        <View style={styles.searchContainer}>
          <Ionicons name="search" size={20} color={COLORS.maroon} style={styles.searchIcon} />
          <TextInput
            placeholder="Search Location"
            style={styles.searchInput}
            placeholderTextColor={COLORS.grey}
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
          {searchQuery.length > 0 && (
            <TouchableOpacity onPress={() => setSearchQuery('')}>
              <Ionicons name="close-circle" size={20} color={COLORS.grey} />
            </TouchableOpacity>
          )}
        </View>


        {/* Category Filter Indicator */}
        {selectedCategory && selectedCategory !== 'all' && (
          <View style={styles.categoryFilterContainer}>
            <Ionicons name="funnel-outline" size={16} color={COLORS.maroon} />
            <Text style={styles.categoryFilterText}>
              Category: {selectedCategory.charAt(0).toUpperCase() + selectedCategory.slice(1)}
            </Text>
            <TouchableOpacity 
              onPress={() => setSelectedCategory(null)}
              style={styles.clearFilterButton}
            >
              <Ionicons name="close-circle" size={18} color={COLORS.maroon} />
            </TouchableOpacity>
          </View>
        )}

        {/* Search Results Info */}
        {searchQuery.length > 0 && (
          <View style={styles.searchInfoContainer}>
            <Text style={styles.searchInfoText}>
              {filteredNodes.length} result{filteredNodes.length !== 1 ? 's' : ''} for "{searchQuery}"
            </Text>
          </View>
        )}

        {/* Map/List Toggle */}
        <View style={styles.toggleContainer}>
          <TouchableOpacity
            style={[styles.toggleButton, viewMode === 'Map' ? styles.toggleActive : styles.toggleInactive]}
            onPress={() => setViewMode('Map')}
          >
            <Text style={[styles.toggleText, viewMode === 'Map' ? styles.toggleTextActive : styles.toggleTextInactive]}>Map</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.toggleButton, viewMode === 'List' ? styles.toggleActive : styles.toggleInactive]}
            onPress={() => setViewMode('List')}
          >
            <Text style={[styles.toggleText, viewMode === 'List' ? styles.toggleTextActive : styles.toggleTextInactive]}>List</Text>
          </TouchableOpacity>
        </View>

        {/* Content Area */}
        {viewMode === 'List' ? (
          <ScrollView contentContainerStyle={styles.listContainer}>
            {loading ? (
              <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color={COLORS.maroon} />
                <Text style={styles.loadingText}>Loading locations...</Text>
              </View>
            ) : filteredNodes.length === 0 ? (
              <View style={styles.emptyContainer}>
                <Ionicons name="search-outline" size={64} color={COLORS.grey} />
                <Text style={styles.emptyTitle}>
                  {searchQuery ? 'No results found' : 'No locations available'}
                </Text>
                <Text style={styles.emptyMessage}>
                  {searchQuery
                    ? `Try searching for something else`
                    : 'Please check your connection and try again'}
                </Text>
                {searchQuery && (
                  <TouchableOpacity
                    style={styles.clearButton}
                    onPress={() => setSearchQuery('')}
                  >
                    <Text style={styles.clearButtonText}>Clear Search</Text>
                  </TouchableOpacity>
                )}
              </View>
            ) : (
              <>
                {filteredNodes.map((node, index) => (
                  <LocationCard
                    key={node?.properties?.id || node?.id || `node-${index}`}
                    node={node}
                    onGetDirections={handleGetDirections}
                    onBookmark={handleBookmark}
                    isBookmarked={isBookmarked(node)}
                  />
                ))}
              </>
            )}
          </ScrollView>
        ) : (
          <View style={{ flex: 1, borderRadius: 15, overflow: 'hidden' }}>
            <MapViewScreen selectedNode={selectedNode} startCoordinate={startCoordinate} />
          </View>
        )}
      </View>

      {/* Location Picker Modal */}
      {showLocationPicker && (
        <View style={styles.locationPickerModal}>
          <LocationPickerScreen
            onLocationSelected={handleLocationSelected}
            onCancel={handleCancelLocationPicker}
            initialCoordinate={startCoordinate}
          />
        </View>
      )}
    </View>
  );
}

// --- Styles ---
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.maroon,
  },
  headerTitleText: {
    color: COLORS.white,
    fontSize: 20,
    fontWeight: 'bold',
  },
  mainContent: {
    flex: 1,
    backgroundColor: COLORS.white,
    borderTopLeftRadius: 30,
    borderTopRightRadius: 30,
    paddingTop: 20,
    paddingHorizontal: 20,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.white,
    borderRadius: 25,
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderColor: COLORS.maroon,
    borderWidth: 1,
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
    color: COLORS.dark,
    marginLeft: 10,
  },
  searchIcon: {
    color: COLORS.maroon,
  },
  categoryFilterContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.pink,
    borderRadius: 20,
    paddingVertical: 8,
    paddingHorizontal: 15,
    marginTop: 10,
    gap: 8,
  },
  categoryFilterText: {
    fontSize: 14,
    color: COLORS.maroon,
    fontWeight: '600',
    flex: 1,
  },
  clearFilterButton: {
    padding: 2,
  },
  searchInfoContainer: {
    paddingVertical: 10,
    paddingHorizontal: 5,
  },
  searchInfoText: {
    fontSize: 14,
    color: COLORS.grey,
    fontWeight: '500',
  },
  toggleContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginVertical: 20,
    alignSelf: 'center',
  },
  toggleButton: {
    paddingVertical: 10,
    paddingHorizontal: 40,
    borderRadius: 25,
    borderWidth: 1,
    marginHorizontal: 5,
  },
  toggleActive: {
    backgroundColor: COLORS.maroon,
    borderColor: COLORS.maroon,
  },
  toggleInactive: {
    backgroundColor: COLORS.white,
    borderColor: COLORS.maroon,
  },
  toggleText: {
    fontSize: 16,
    fontWeight: '600',
  },
  toggleTextActive: {
    color: COLORS.white,
  },
  toggleTextInactive: {
    color: COLORS.maroon,
  },
  listContainer: {
    paddingBottom: 100,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  loadingText: {
    marginTop: 15,
    fontSize: 16,
    color: COLORS.grey,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
    paddingHorizontal: 40,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: COLORS.dark,
    marginTop: 20,
    marginBottom: 10,
  },
  emptyMessage: {
    fontSize: 14,
    color: COLORS.grey,
    textAlign: 'center',
    lineHeight: 20,
  },
  clearButton: {
    marginTop: 20,
    paddingVertical: 10,
    paddingHorizontal: 30,
    borderRadius: 25,
    borderWidth: 1,
    borderColor: COLORS.maroon,
  },
  clearButtonText: {
    color: COLORS.maroon,
    fontSize: 14,
    fontWeight: '600',
  },
  locationButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: COLORS.maroon,
    borderRadius: 25,
    paddingVertical: 12,
    paddingHorizontal: 20,
    marginTop: 12,
    gap: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  locationButtonText: {
    color: COLORS.white,
    fontSize: 16,
    fontWeight: '600',
  },
  locationPickerModal: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    zIndex: 1000,
  },
});
