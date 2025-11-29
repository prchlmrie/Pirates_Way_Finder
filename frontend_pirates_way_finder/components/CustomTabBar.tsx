// components/CustomTabBar.tsx
import { Ionicons } from '@expo/vector-icons';
import { BottomTabBarProps } from '@react-navigation/bottom-tabs';
import React, { useEffect, useRef } from 'react';
import { Animated, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { categories, useCategory } from '../CategoryContext';

const COLORS = {
  maroon: '#8B0000',
  pink: '#FFE5E5',
  grey: '#B0B0B0',
  white: '#FFFFFF',
};

const tabIcons: Record<string, React.ComponentProps<typeof Ionicons>['name']> = {
  home: 'home',
  favorite: 'heart',
  rating: 'star',
};

// --- FloatingCategoryPills component ---
const FloatingCategoryPills = ({ 
  isOpen, 
  onCategoryPress 
}: { 
  isOpen: boolean;
  onCategoryPress: (category: string) => void;
}) => {
  const slideAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(slideAnim, {
      toValue: isOpen ? 1 : 0,
      duration: 300,
      useNativeDriver: true,
    }).start();
  }, [isOpen, slideAnim]);

  const animatedStyle = {
    opacity: slideAnim,
    transform: [
      {
        translateY: slideAnim.interpolate({
          inputRange: [0, 1],
          outputRange: [50, 0],
        }),
      },
    ],
  };

  return (
    <Animated.View 
      style={[styles.pillsContainer, animatedStyle]}
      pointerEvents={isOpen ? 'auto' : 'none'} 
    >
      {categories.map((cat) => (
        <TouchableOpacity 
          key={cat.name} 
          style={styles.pillButton}
          onPress={() => onCategoryPress(cat.name.toLowerCase())}
        >
          <Ionicons name={cat.icon as any} size={18} color={cat.color} />
          <Text style={styles.pillText}>{cat.name}</Text>
        </TouchableOpacity>
      ))}
    </Animated.View>
  );
};


export default function CustomTabBar({ state, descriptors, navigation }: BottomTabBarProps) {
  const { isCategoriesOpen, toggleCategories, setSelectedCategory, isMapViewActive } = useCategory();

  const handleCategoryPress = (category: string) => {
    console.log(`🏷️ Category selected: ${category}`);
    // Set the selected category in context
    setSelectedCategory(category);
    // Navigate to home screen (where search bar and filtering happen)
    navigation.navigate('home');
    // Close the pills
    toggleCategories();
  };

  // Hide the entire tab bar when map view is active
  if (isMapViewActive) {
    return null;
  }

  return (
    // This container holds both the tab bar AND the pills
    <View style={styles.container}>
      
      {/* Render the pills unconditionally.
        We pass 'isCategoriesOpen' as a prop to let the component
        manage its own animation.
      */}
      <FloatingCategoryPills 
        isOpen={isCategoriesOpen} 
        onCategoryPress={handleCategoryPress}
      />

      {/* The light pink background bar */}
      <View style={styles.tabBar}>
        
        {/* The big red 'X' or 'Grid' button */}
        <TouchableOpacity
          onPress={toggleCategories}
          style={styles.categoriesButton}
        >
          <Ionicons
            name={isCategoriesOpen ? 'close' : 'apps'}
            size={32}
            color={COLORS.white}
          />
        </TouchableOpacity>

        {/* Regular tab buttons (Home, Favorite, Rating) */}
        {state.routes.map((route, index) => {
          if (route.name === 'categories') return null; // Skip categories

          const { options } = descriptors[route.key];
          const label = options.title !== undefined ? String(options.title) : route.name;
          const isFocused = state.index === index;

          return (
            <TouchableOpacity
              key={route.key}
              onPress={() => navigation.navigate(route.name)}
              style={styles.tabButton}
            >
              <Ionicons
                name={tabIcons[route.name]}
                size={24}
                color={isFocused ? COLORS.maroon : COLORS.grey}
              />
              <Text style={{ color: isFocused ? COLORS.maroon : COLORS.grey, fontSize: 10 }}>
                {label}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    bottom: 20,
    left: 20,
    right: 20,
    height: 80, 
    alignItems: 'center', 
  },
  tabBar: {
    position: 'absolute',
    bottom: 0,
    flexDirection: 'row',
    height: 65,
    backgroundColor: COLORS.pink,
    borderRadius: 35,
    paddingLeft: 80, 
    paddingRight: 15,
    alignItems: 'center',
    justifyContent: 'space-around',
    width: '100%',
    elevation: 8,
  },
  categoriesButton: {
    position: 'absolute',
    left: -10,
    top: -8,
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: COLORS.maroon,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 5,
    borderColor: '#f6f6f6',
    elevation: 10,
  },
  tabButton: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },

  // --- Styles for Pills ---
  pillsContainer: {
    position: 'absolute',
    left: 0,
    bottom: 90, // Position it just above the 80-unit high container
    alignItems: 'flex-start',
  },
  pillButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.pink,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 20,
    marginBottom: 15,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
  },
  pillText: {
    color: COLORS.maroon,
    marginLeft: 8,
    fontWeight: '600',
  },
});