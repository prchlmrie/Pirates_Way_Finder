// app/(tabs)/categories.tsx
import { Ionicons } from '@expo/vector-icons';
import { Stack, useRouter } from 'expo-router';
import React, { useEffect, useState } from 'react';
import { ActivityIndicator, Image, ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import MapViewScreen from '../components/MapViewScreen';
import LocationCard from '../../components/ui/LocationCard';
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
  blue: '#3498db',
  red: '#e74c3c',
  purple: '#9b59b6',
  green: '#27ae60',
};

// Category Configuration
const CATEGORIES = [
  { id: 'office', name: 'Office', icon: 'briefcase-outline', color: COLORS.blue },
  { id: 'classroom', name: 'Classroom', icon: 'school-outline', color: COLORS.red },
  { id: 'laboratory', name: 'Laboratory', icon: 'flask-outline', color: COLORS.purple },
  { id: 'amenity', name: 'Amenity', icon: 'restaurant-outline', color: COLORS.green },
];

// --- Custom Header Component ---
function HeaderTitle() {
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center' }}>
      <Image
        source={require('../../assets/pirate-logo.png')} 
        style={{ width: 40, height: 40, marginRight: 10 }}
        resizeMode="contain"
      />
      <Text style={styles.headerTitleText}>Categories</Text>
    </View>
  );
}

// Test starting coordinate (for pathfinding)
// Starting point at (504, 2302) - main entrance area
const TEST_START_COORDINATE = { x: 504, y: 2302 };

export default function CategoriesScreen() {
  const router = useRouter();
  const { isBookmarked, toggleBookmark } = useBookmarks();
  const { selectedCategory: contextCategory, setSelectedCategory: setContextCategory } = useCategory();
  const [viewMode, setViewMode] = useState('List');
  const [localSelectedCategory, setLocalSelectedCategory] = useState(contextCategory);
  const [allNodes, setAllNodes] = useState([]);
  const [filteredNodes, setFilteredNodes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);

  // Fetch nodes from API on component mount
  useEffect(() => {
    fetchNodesData();
  }, []);

  // Sync with context category when it changes (from CustomTabBar)
  useEffect(() => {
    if (contextCategory) {
      console.log(`📱 Categories screen received category: ${contextCategory}`);
      setLocalSelectedCategory(contextCategory);
    }
  }, [contextCategory]);

  // Filter nodes by selected category
  useEffect(() => {
    if (localSelectedCategory) {
      filterByCategory();
    } else {
      setFilteredNodes([]);
    }
  }, [localSelectedCategory, allNodes]);

  const fetchNodesData = async () => {
    try {
      setLoading(true);
      const data = await getNodes();
      
      // Filter to only show nodes with categories
      const categorizedNodes = data.filter(node => {
        const category = node?.properties?.category?.toLowerCase();
        return ['office', 'classroom', 'laboratory', 'amenity'].includes(category);
      });
      
      setAllNodes(categorizedNodes);
      console.log(`✅ Loaded ${categorizedNodes.length} locations`);
    } catch (error) {
      console.error('❌ Error fetching nodes:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterByCategory = () => {
    if (!localSelectedCategory) {
      setFilteredNodes([]);
      return;
    }

    const filtered = allNodes.filter(node => {
      const category = node?.properties?.category?.toLowerCase();
      return category === localSelectedCategory.toLowerCase();
    });

    // Sort alphabetically by name
    filtered.sort((a, b) => {
      const nameA = (a?.properties?.name || a?.name || '').toLowerCase();
      const nameB = (b?.properties?.name || b?.name || '').toLowerCase();
      return nameA.localeCompare(nameB);
    });

    setFilteredNodes(filtered);
    console.log(`🏷️ Filtered ${filtered.length} locations for category: ${localSelectedCategory}`);
  };

  const handleCategorySelect = (categoryId) => {
    if (localSelectedCategory === categoryId) {
      // Toggle off if clicking the same category
      setLocalSelectedCategory(null);
      setContextCategory(null);
    } else {
      setLocalSelectedCategory(categoryId);
      setContextCategory(categoryId);
    }
  };

  const handleGetDirections = (node) => {
    console.log('🧭 Getting directions to:', node?.properties?.name);
    setSelectedNode(node);
    setViewMode('Map');
  };

  const handleBookmark = (node) => {
    toggleBookmark(node);
  };

  const getCategoryStats = (categoryId) => {
    return allNodes.filter(node => {
      const category = node?.properties?.category?.toLowerCase();
      return category === categoryId.toLowerCase();
    }).length;
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
        {/* Category Pills */}
        <ScrollView 
          horizontal 
          showsHorizontalScrollIndicator={false}
          style={styles.categoryPillsContainer}
          contentContainerStyle={styles.categoryPillsContent}
        >
          {CATEGORIES.map((category) => {
            const isActive = localSelectedCategory === category.id;
            const count = getCategoryStats(category.id);
            
            return (
              <TouchableOpacity
                key={category.id}
                style={[
                  styles.categoryPill,
                  isActive && { ...styles.categoryPillActive, backgroundColor: category.color }
                ]}
                onPress={() => handleCategorySelect(category.id)}
                activeOpacity={0.7}
              >
                <Ionicons 
                  name={category.icon} 
                  size={20} 
                  color={isActive ? COLORS.white : category.color} 
                />
                <Text style={[
                  styles.categoryPillText,
                  isActive && styles.categoryPillTextActive
                ]}>
                  {category.name}
                </Text>
                <View style={[
                  styles.categoryCountBadge,
                  isActive && styles.categoryCountBadgeActive
                ]}>
                  <Text style={[
                    styles.categoryCountText,
                    isActive && styles.categoryCountTextActive
                  ]}>
                    {count}
                  </Text>
                </View>
              </TouchableOpacity>
            );
          })}
        </ScrollView>

        {/* Map/List Toggle */}
        {localSelectedCategory && (
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
        )}

        {/* Content Area */}
        {!localSelectedCategory ? (
          <View style={styles.emptyContainer}>
            <Ionicons name="apps-outline" size={64} color={COLORS.grey} />
            <Text style={styles.emptyTitle}>Select a Category</Text>
            <Text style={styles.emptyMessage}>
              Choose a category above to browse locations
            </Text>
          </View>
        ) : viewMode === 'List' ? (
          <ScrollView contentContainerStyle={styles.listContainer}>
            {loading ? (
              <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color={COLORS.maroon} />
                <Text style={styles.loadingText}>Loading locations...</Text>
              </View>
            ) : filteredNodes.length === 0 ? (
              <View style={styles.emptyContainer}>
                <Ionicons name="folder-open-outline" size={64} color={COLORS.grey} />
                <Text style={styles.emptyTitle}>No Locations Found</Text>
                <Text style={styles.emptyMessage}>
                  No locations in this category yet
                </Text>
              </View>
            ) : (
              <>
                <View style={styles.resultsHeaderContainer}>
                  <Text style={styles.resultsHeaderText}>
                    {filteredNodes.length} {localSelectedCategory} location{filteredNodes.length !== 1 ? 's' : ''}
                  </Text>
                </View>
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
            <MapViewScreen selectedNode={selectedNode} startCoordinate={TEST_START_COORDINATE} />
          </View>
        )}
      </View>
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
  },
  categoryPillsContainer: {
    maxHeight: 70,
    paddingHorizontal: 20,
    marginBottom: 10,
  },
  categoryPillsContent: {
    alignItems: 'center',
    paddingRight: 20,
  },
  categoryPill: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.white,
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 25,
    marginRight: 10,
    borderWidth: 2,
    borderColor: COLORS.lightGrey,
    gap: 8,
  },
  categoryPillActive: {
    borderColor: 'transparent',
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  categoryPillText: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.dark,
  },
  categoryPillTextActive: {
    color: COLORS.white,
  },
  categoryCountBadge: {
    backgroundColor: COLORS.lightGrey,
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
    minWidth: 24,
    alignItems: 'center',
  },
  categoryCountBadgeActive: {
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
  },
  categoryCountText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: COLORS.dark,
  },
  categoryCountTextActive: {
    color: COLORS.white,
  },
  toggleContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginVertical: 15,
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
    paddingHorizontal: 20,
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
  resultsHeaderContainer: {
    paddingVertical: 10,
    paddingHorizontal: 5,
    marginBottom: 10,
  },
  resultsHeaderText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.dark,
    textTransform: 'capitalize',
  },
});
