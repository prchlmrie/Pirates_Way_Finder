// app/(tabs)/favorite.tsx
import { Ionicons } from '@expo/vector-icons';
import { Stack, useRouter } from 'expo-router';
import React, { useEffect, useState } from 'react';
import { ActivityIndicator, Image, ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import MapViewScreen from '../components/MapViewScreen';
import LocationCard from '../../components/ui/LocationCard';
import { getNodes } from '../../api/mapApi';
import { useBookmarks } from '../../contexts/BookmarkContext';

// --- Define Colors ---
const COLORS = {
  maroon: '#8B0000',
  white: '#FFFFFF',
  lightGrey: '#F4F4F4',
  grey: '#B0B0B0',
  dark: '#333333',
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
      <Text style={styles.headerTitleText}>My Favorites</Text>
    </View>
  );
}

// Test starting coordinate (for pathfinding)
// Starting point at (504, 2302) - main entrance area
const TEST_START_COORDINATE = { x: 504, y: 2302 };

export default function FavoriteScreen() {
  const router = useRouter();
  const { isBookmarked, toggleBookmark, getBookmarkedNodeIds, loading: bookmarksLoading } = useBookmarks();
  const [viewMode, setViewMode] = useState('List');
  const [allNodes, setAllNodes] = useState([]);
  const [favoriteNodes, setFavoriteNodes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);

  // Fetch nodes from API on component mount
  useEffect(() => {
    fetchNodesData();
  }, []);

  // Filter to show only bookmarked nodes
  useEffect(() => {
    if (!bookmarksLoading && allNodes.length > 0) {
      filterFavorites();
    }
  }, [allNodes, bookmarksLoading, getBookmarkedNodeIds().length]);

  const fetchNodesData = async () => {
    try {
      setLoading(true);
      const data = await getNodes();
      
      // Filter to only show nodes with relevant categories (office, classroom, laboratory, amenity)
      const relevantNodes = data.filter(node => {
        const category = node?.properties?.category?.toLowerCase();
        return ['office', 'classroom', 'laboratory', 'amenity'].includes(category);
      });
      
      setAllNodes(relevantNodes);
      console.log(`✅ Loaded ${relevantNodes.length} locations`);
    } catch (error) {
      console.error('❌ Error fetching nodes:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterFavorites = () => {
    const bookmarkedIds = getBookmarkedNodeIds();
    const favorites = allNodes.filter(node => {
      const nodeId = node?.properties?.id || node?.id;
      return bookmarkedIds.includes(nodeId);
    });
    
    // Sort alphabetically by name
    favorites.sort((a, b) => {
      const nameA = (a?.properties?.name || a?.name || '').toLowerCase();
      const nameB = (b?.properties?.name || b?.name || '').toLowerCase();
      return nameA.localeCompare(nameB);
    });
    
    setFavoriteNodes(favorites);
    console.log(`❤️ ${favorites.length} favorites found`);
  };

  const handleGetDirections = (node) => {
    console.log('🧭 Getting directions to:', node?.properties?.name);
    setSelectedNode(node);
    setViewMode('Map');
  };

  const handleBookmark = (node) => {
    toggleBookmark(node);
    // Re-filter after a short delay to allow state to update
    setTimeout(() => filterFavorites(), 100);
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

      <View style={styles.mainContent}>
        {/* Map/List Toggle */}
        <View style={styles.toggleContainer}>
          <TouchableOpacity
            style={[styles.toggleButton, viewMode === 'Map' ? styles.toggleActive : {}]}
            onPress={() => setViewMode('Map')}
          >
            <Text style={[styles.toggleText, viewMode === 'Map' ? styles.toggleTextActive : {}]}>Map</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.toggleButton, viewMode === 'List' ? styles.toggleActive : {}]}
            onPress={() => setViewMode('List')}
          >
            <Text style={[styles.toggleText, viewMode === 'List' ? styles.toggleTextActive : {}]}>List</Text>
          </TouchableOpacity>
        </View>

        {/* Combined Content Area */}
        {viewMode === 'List' ? (
          <ScrollView contentContainerStyle={styles.listContainer}>
            {loading || bookmarksLoading ? (
              <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color={COLORS.maroon} />
                <Text style={styles.loadingText}>Loading favorites...</Text>
              </View>
            ) : favoriteNodes.length === 0 ? (
              <View style={styles.emptyContainer}>
                <Ionicons name="heart-outline" size={64} color={COLORS.grey} />
                <Text style={styles.emptyTitle}>No Favorites Yet</Text>
                <Text style={styles.emptyMessage}>
                  Tap the heart icon on any location to add it to your favorites!
                </Text>
                <TouchableOpacity
                  style={styles.goToHomeButton}
                  onPress={() => router.push('/(tabs)/home')}
                >
                  <Text style={styles.goToHomeButtonText}>Browse Locations</Text>
                </TouchableOpacity>
              </View>
            ) : (
              <>
                <View style={styles.favoriteHeaderContainer}>
                  <Text style={styles.favoriteHeaderText}>
                    ❤️ {favoriteNodes.length} Favorite{favoriteNodes.length !== 1 ? 's' : ''}
                  </Text>
                </View>
                {favoriteNodes.map((node, index) => (
                  <LocationCard
                    key={node?.properties?.id || node?.id || `node-${index}`}
                    node={node}
                    onGetDirections={handleGetDirections}
                    onBookmark={handleBookmark}
                    isBookmarked={true}
                  />
                ))}
              </>
            )}
          </ScrollView>
        ) : (
          <View style={{ flex: 1, borderRadius: 15, overflow: 'hidden' }}>
            <MapViewScreen selectedNode={selectedNode} startCoordinate={TEST_START_COORDINATE} />
          </View>
        )}
      </View>
    </View>
  );
}

// --- Styles for FavoriteScreen ---
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
    borderColor: COLORS.maroon,
    marginHorizontal: 5,
  },
  toggleActive: {
    backgroundColor: COLORS.maroon,
  },
  toggleText: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.maroon,
  },
  toggleTextActive: {
    color: COLORS.white,
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
  goToHomeButton: {
    marginTop: 20,
    paddingVertical: 12,
    paddingHorizontal: 30,
    borderRadius: 25,
    backgroundColor: COLORS.maroon,
  },
  goToHomeButtonText: {
    color: COLORS.white,
    fontSize: 14,
    fontWeight: '600',
  },
  favoriteHeaderContainer: {
    paddingVertical: 10,
    paddingHorizontal: 5,
    marginBottom: 10,
  },
  favoriteHeaderText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.dark,
  },
});
