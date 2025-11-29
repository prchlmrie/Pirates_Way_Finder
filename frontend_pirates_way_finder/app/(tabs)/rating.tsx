// app/(tabs)/rating.tsx
import { Ionicons } from '@expo/vector-icons';
import Slider from '@react-native-community/slider';
import { Stack, useRouter } from 'expo-router';
import React, { useEffect, useState } from 'react';
import { ActivityIndicator, Alert, Image, ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';
import SelectDropdown from 'react-native-select-dropdown';
import { getNodes } from '../../api/mapApi';

const COLORS = {
  maroon: '#8B0000', 
  bad: '#E57373', 
  badDark: '#D32F2F',
  notBad: '#FFF176',
  notBadDark: '#FBC02D',
  good: '#81C784',
  goodDark: '#388E38',
  white: '#FFFFFF',
  grey: '#B0B0B0',
  dark: '#333333',
  lightGrey: '#F4F4F4',
};

type RatingState = 'BAD' | 'NOT BAD' | 'GOOD';

const getRatingStyle = (value: number): { state: RatingState; bgColor: string; darkColor: string; thumbColor: string; } => {
  if (value < 33) return { state: 'BAD', bgColor: COLORS.bad, darkColor: COLORS.badDark, thumbColor: COLORS.badDark };
  if (value < 67) return { state: 'NOT BAD', bgColor: COLORS.notBad, darkColor: COLORS.notBadDark, thumbColor: COLORS.notBadDark };
  return { state: 'GOOD', bgColor: COLORS.good, darkColor: COLORS.goodDark, thumbColor: COLORS.goodDark };
};

function HeaderTitle() {
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center' }}>
      <Image source={require('../../assets/pirate-logo.png')} style={{ width: 40, height: 40, marginRight: 10 }} resizeMode="contain" />
      <Text style={styles.headerTitleText}>Pirates Way Finder</Text>
    </View>
  );
}

const RatingFace = ({ state, color }: { state: RatingState, color: string }) => {
  return (
    <View style={styles.faceContainer}>
      <View style={[styles.eye, { backgroundColor: color }]} />
      <View style={[styles.eye, { backgroundColor: color }]} />
      {state === 'BAD' && <View style={[styles.mouthFrown, { borderTopColor: color }]} />}
      {state === 'NOT BAD' && <View style={[styles.mouthStraight, { backgroundColor: color }]} />}
      {state === 'GOOD' && <View style={[styles.mouthSmile, { borderTopColor: color }]} />}
    </View>
  );
};

export default function RatingScreen() {
  const router = useRouter(); 
  const [ratingValue, setRatingValue] = useState(50);
  const [selectedService, setSelectedService] = useState<any>(null); 
  const [note, setNote] = useState('');
  const [locations, setLocations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const { state, bgColor, darkColor, thumbColor } = getRatingStyle(ratingValue);

  // Fetch nodes from backend
  useEffect(() => {
    fetchLocations();
  }, []);

  const fetchLocations = async () => {
    try {
      setLoading(true);
      const data = await getNodes();
      
      // Filter to only show relevant categories
      const relevantNodes = data.filter(node => {
        const category = node?.properties?.category?.toLowerCase();
        return ['office', 'classroom', 'laboratory', 'amenity', 'library'].includes(category);
      });
      
      setLocations(relevantNodes);
      console.log(`✅ Loaded ${relevantNodes.length} locations for rating`);
    } catch (error) {
      console.error('❌ Error fetching locations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!selectedService) {
      Alert.alert('Missing Info', 'Please select an office or service to rate.');
      return;
    }
    
    const serviceName = selectedService?.properties?.name || selectedService?.name || 'Unknown';
    const locationId = selectedService?.properties?.id || selectedService?.id || '';
    const buildingName = selectedService?.properties?.building_name || null;
    
    try {
      const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';
      
      const response = await fetch(`${API_BASE_URL}/ratings/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          location_id: locationId,
          location_name: serviceName,
          building_name: buildingName,
          rating: state,
          comment: note || null,
        }),
      });
      
      if (response.ok) {
        Alert.alert(
          'Feedback Submitted',
          `Thank you for your feedback!\n\nOffice: ${serviceName}\nRating: ${state}`
        );
        
        // Reset form
        setRatingValue(50);
        setSelectedService(null);
        setNote('');
      } else {
        throw new Error('Failed to submit rating');
      }
    } catch (error) {
      console.error('Error submitting rating:', error);
      Alert.alert(
        'Error',
        'Failed to submit your rating. Please try again later.'
      );
    }
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
            <TouchableOpacity onPress={() => alert('About/Info page pressed!')} style={{ marginRight: 15 }}>
              <Ionicons name="information-circle-outline" size={30} color={COLORS.white} />
            </TouchableOpacity>
          ),
        }}
      />
      
      <View style={styles.mainContent}> 
        <ScrollView contentContainerStyle={styles.scrollContent}>
          
          <View style={{ marginBottom: 20, zIndex: 1000 }}>
            <Text style={styles.label}>HOW WAS YOUR EXPERIENCE?{"\n"}Choose an office / facility below!</Text>
            
            {loading ? (
              <View style={styles.loadingContainer}>
                <ActivityIndicator size="small" color={COLORS.maroon} />
                <Text style={styles.loadingText}>Loading locations...</Text>
              </View>
            ) : (
              <SelectDropdown
                data={locations}
                onSelect={(selectedItem: any, index: number) => {
                  setSelectedService(selectedItem); 
                }}
                renderButton={(selectedItem: any | null, isOpened: boolean) => (
                  <View style={styles.dropdownButton}>
                    <Text style={styles.dropdownButtonText}>
                      {selectedItem 
                        ? (selectedItem?.properties?.name || selectedItem?.name || 'Unknown') 
                        : 'Select an office or service...'}
                    </Text>
                    <Ionicons name={isOpened ? 'chevron-up' : 'chevron-down'} size={20} color={COLORS.grey} style={{ marginLeft: 10 }} />
                  </View>
                )}
                renderItem={(item: any, index: number, isSelected: boolean) => (
                  <View style={[styles.dropdownRow, { backgroundColor: isSelected ? COLORS.lightGrey : COLORS.white }]}>
                    <Text style={styles.dropdownRowText}>
                      {item?.properties?.name || item?.name || 'Unknown'}
                    </Text>
                  </View>
                )}
                dropdownStyle={styles.dropdownMenu}
              />
            )}
          </View>

          <View style={[styles.ratingCard, { backgroundColor: bgColor }]}>
            <View style={styles.cardHeader}>
              <TouchableOpacity onPress={() => Alert.alert('Info', 'Rate your experience with the selected service. Slide to adjust your rating!')}>
                <Ionicons name="information-circle" size={24} color={darkColor} />
              </TouchableOpacity>
            </View>
            
            <RatingFace state={state} color={darkColor} />
            <Text style={[styles.ratingText, { color: darkColor }]}>{state}</Text>

            <Slider
              style={styles.slider}
              value={ratingValue}
              minimumValue={0}
              maximumValue={100}
              minimumTrackTintColor={darkColor}
              maximumTrackTintColor={COLORS.white}
              thumbTintColor={thumbColor}
              onValueChange={setRatingValue}
            />

            <TextInput
              style={[styles.noteInput, { borderColor: darkColor, color: darkColor }]}
              placeholder="Add Note (optional)"
              placeholderTextColor={darkColor}
              value={note}
              onChangeText={setNote}
              multiline
            />

            <TouchableOpacity style={[styles.submitButton, { backgroundColor: darkColor }]} onPress={handleSubmit}>
              <Text style={styles.submitButtonText}>Submit</Text>
              <Ionicons name="arrow-forward" size={16} color={COLORS.white} />
            </TouchableOpacity>
          </View>
        </ScrollView>
      </View> 
    </View>
  );
}

// --- Styles ---
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.maroon },
  headerTitleText: { color: COLORS.white, fontSize: 20, fontWeight: 'bold' },
  mainContent: { flex: 1, backgroundColor: '#f6f6f6', borderTopLeftRadius: 30, borderTopRightRadius: 30 },
  scrollContent: { padding: 20, paddingBottom: 120 },
  label: { fontSize: 16, fontWeight: '600', color: COLORS.dark, marginBottom: 10 },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 15,
    backgroundColor: COLORS.white,
    borderRadius: 8,
  },
  loadingText: {
    marginLeft: 10,
    fontSize: 14,
    color: COLORS.grey,
  },
  ratingCard: { flex: 1, borderRadius: 30, padding: 20, alignItems: 'center', marginTop: 20, elevation: 5, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4 },
  cardHeader: { flexDirection: 'row', justifyContent: 'flex-end', width: '100%' },
  faceContainer: { width: 200, height: 100, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', marginTop: 30, marginBottom: 20, position: 'relative' },
  eye: { width: 60, height: 60, borderRadius: 30, marginHorizontal: 15 },
  mouthFrown: { width: 100, height: 50, borderRadius: 50, borderTopWidth: 10, position: 'absolute', bottom: 0 },
  mouthStraight: { width: 100, height: 10, borderRadius: 5, position: 'absolute', bottom: 0 },
  mouthSmile: { width: 100, height: 50, borderRadius: 50, borderTopWidth: 10, position: 'absolute', bottom: 0, transform: [{ rotate: '180deg' }] },
  ratingText: { fontSize: 32, fontWeight: 'bold', textTransform: 'uppercase', letterSpacing: 2, marginVertical: 20 },
  slider: { width: '100%', height: 40, marginVertical: 20 },
  noteInput: { width: '100%', minHeight: 50, borderBottomWidth: 2, paddingHorizontal: 10, fontSize: 16, marginVertical: 20, color: COLORS.dark },
  submitButton: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 15, paddingHorizontal: 30, borderRadius: 30, width: '100%', marginTop: 10 },
  submitButtonText: { color: COLORS.white, fontSize: 16, fontWeight: 'bold', marginRight: 10 },
  dropdownButton: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', width: '100%', height: 50, backgroundColor: COLORS.white, borderRadius: 8, borderWidth: 1, borderColor: COLORS.grey, paddingHorizontal: 10 },
  dropdownButtonText: { color: COLORS.dark, fontSize: 16, textAlign: 'left', flex: 1 },
  dropdownMenu: { backgroundColor: COLORS.white, borderRadius: 8, marginTop: 2 },
  dropdownRow: { flexDirection: 'row', alignItems: 'center', backgroundColor: COLORS.white, borderBottomColor: COLORS.lightGrey, borderBottomWidth: 1, height: 50, paddingHorizontal: 10 },
  dropdownRowText: { color: COLORS.dark, fontSize: 16, textAlign: 'left' },
});
