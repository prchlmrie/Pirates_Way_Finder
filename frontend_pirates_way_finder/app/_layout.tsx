// app/_layout.tsx
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { CategoryProvider } from '../CategoryContext'; // Import from root
import { BookmarkProvider } from '../contexts/BookmarkContext';

const COLORS = {
  maroon: '#8B0000',
  white: '#FFFFFF',
};

export default function RootLayout() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      {/* Wrap your entire app with the providers */}
      <BookmarkProvider>
        <CategoryProvider> 
          <StatusBar style="light" />
        <Stack
          screenOptions={{
            headerStyle: { backgroundColor: COLORS.maroon },
            headerTintColor: COLORS.white,
            headerTitleAlign: 'center',
          }}
        >
          {/* The Welcome screen. No header. */}
          <Stack.Screen name="index" options={{ headerShown: false }} />
          
          {/* The main app (tabs). No header. */}
          <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
          
          {/* The Admin screen. Opens as a modal. */}
          <Stack.Screen 
            name="adminLogin" 
            options={{ 
              presentation: 'modal',
              title: 'Admin Login',
            }} 
          />
          {/* You can remove your old 'modal.tsx' file if you don't use it */}
        </Stack>
        </CategoryProvider>
      </BookmarkProvider>
    </GestureHandlerRootView>
  );
}