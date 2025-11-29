// CategoryContext.tsx
// This context manages category filtering and favorites for the app
// Compatible with both backend data and UI design
import React, { createContext, ReactNode, useContext, useState } from 'react';

// --- Define and Export Category Configuration ---
// Categories available for filtering
export const categories = [
  { name: 'Office', icon: 'briefcase-outline', color: '#2E7D32' },
  { name: 'Laboratory', icon: 'flask-outline', color: '#D81B60' },
  { name: 'Amenity', icon: 'restaurant-outline', color: '#F9A825' },
  { name: 'Classroom', icon: 'school-outline', color: '#e74c3c' },
];

// --- Define the shape of the context ---
interface CategoryContextType {
  isCategoriesOpen: boolean;
  filterCategory: string;
  favorites: string[]; 
  toggleCategories: () => void;
  setFilter: (category: string) => void;
  toggleFavorite: (locationId: string) => void;
  // Map view state management
  selectedCategory: string | null;
  setSelectedCategory: (category: string | null) => void;
  isMapViewActive: boolean;
  setIsMapViewActive: (isActive: boolean) => void;
}

const CategoryContext = createContext<CategoryContextType | undefined>(undefined);

export const CategoryProvider = ({ children }: { children: ReactNode }) => {
  const [isCategoriesOpen, setIsCategoriesOpen] = useState(false);
  const [filterCategory, setFilterCategory] = useState('All');
  const [favorites, setFavorites] = useState<string[]>([]); 
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [isMapViewActive, setIsMapViewActive] = useState(false);

  const toggleCategories = () => {
    setIsCategoriesOpen(prev => {
      if (prev) {
        setFilterCategory('All');
      }
      return !prev;
    });
  };

  const setFilter = (category: string) => {
    setFilterCategory(category);
    setIsCategoriesOpen(false);
    setSelectedCategory(category === 'All' ? null : category);
  };

  const toggleFavorite = (locationId: string) => {
    setFavorites(prevFavorites => {
      if (prevFavorites.includes(locationId)) {
        return prevFavorites.filter(id => id !== locationId);
      } else {
        return [...prevFavorites, locationId];
      }
    });
  };

  return (
    <CategoryContext.Provider 
      value={{ 
        isCategoriesOpen, 
        toggleCategories, 
        filterCategory, 
        setFilter,
        favorites,
        toggleFavorite,
        selectedCategory,
        setSelectedCategory,
        isMapViewActive,
        setIsMapViewActive,
      }}
    >
      {children}
    </CategoryContext.Provider>
  );
};

export const useCategory = () => {
  const context = useContext(CategoryContext);
  if (context === undefined) {
    throw new Error('useCategory must be used within a CategoryProvider');
  }
  return context;
};

