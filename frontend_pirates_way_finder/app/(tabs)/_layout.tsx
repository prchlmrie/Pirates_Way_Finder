// app/(tabs)/_layout.tsx
import { Tabs } from 'expo-router';
import React from 'react';
import CustomTabBar from '../../components/CustomTabBar'; // Import the custom bar

export default function TabsLayout() {
  return (
    <Tabs
      // Use the tabBar prop to render our custom component
      tabBar={props => <CustomTabBar {...props} />}
      screenOptions={{
        headerShown: false, // Headers are handled inside each screen
      }}
    >
      {/* These 4 routes MUST exist for the tab bar to work */}
      <Tabs.Screen name="categories" options={{ title: 'Categories' }} />
      <Tabs.Screen name="home" options={{ title: 'Home' }} />
      <Tabs.Screen name="favorite" options={{ title: 'Favorite' }} />
      <Tabs.Screen name="rating" options={{ title: 'Rating' }} />
    </Tabs>
  );
}