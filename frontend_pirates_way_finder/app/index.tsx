// app/index.tsx
import { useRouter } from 'expo-router';
import React from 'react';
import { Image, ImageBackground, StyleSheet, Text, TouchableOpacity, View } from 'react-native';

const COLORS = {
  maroon: '#8B0000',
  white: '#FFFFFF',
  redOverlay: 'rgba(139, 0, 0, 0.6)',
};

export default function WelcomeScreen() {
  const router = useRouter();

  const onGetStarted = () => {
    // This replaces the Welcome screen with the Home screen
    // The user can't go "back" to Welcome
    router.replace('/(tabs)/home'); 
  };

  return (
    <ImageBackground
      source={require('../assets/welcome-bg.png')} 
      style={styles.background}
    >
      <View style={styles.overlay}>
        
        <Image
          source={require('../assets/pirate-pin-logo.png')} 
          style={styles.logo}
          resizeMode="contain"
        />

        <Text style={styles.title}>Pirates Way Finder</Text>

        <TouchableOpacity
          style={styles.button}
          onPress={onGetStarted} // Triggers navigation
        >
          <Text style={styles.buttonText}>Get Started</Text>
        </TouchableOpacity>

        <Image
          source={require('../assets/winding-path.png')} 
          style={styles.windingPath}
          resizeMode="contain"
        />
      </View>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  background: {
    flex: 1,
    justifyContent: 'flex-end',
  },
  overlay: {
    flex: 1,
    backgroundColor: COLORS.redOverlay,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  logo: {
    width: 200,
    height: 200,
  },
  title: {
    fontSize: 48,
    fontWeight: 'bold',
    color: COLORS.white,
    textAlign: 'center',
    marginTop: 20,
    marginBottom: 40,
    textShadowColor: 'rgba(0, 0, 0, 0.3)',
    textShadowOffset: { width: 2, height: 2 },
    textShadowRadius: 5,
    zIndex: 2
  },
  button: {
    backgroundColor: COLORS.white,
    paddingVertical: 15,
    paddingHorizontal: 50,
    borderRadius: 30,
    marginBottom: 60,
    elevation: 5,
    zIndex: 2,
  },
  buttonText: {
    color: COLORS.maroon,
    fontSize: 18,
    fontWeight: 'bold',
    zIndex: 2,
  },
  windingPath: {
    width: '200%',
    height: 700,
    position: 'absolute',
    bottom: -300,
    left: -300,
    zIndex: 1,
  },
});