import { useState } from 'react';
import { FaEdit, FaMap, FaMinus, FaPlus } from 'react-icons/fa';
import './ManagePOIs.css';

// --- 1. DEFINE YOUR MAP IMAGES HERE ---
// "Whole Campus Map" is now first, so it will be the default.
const campusMaps = [
  { name: "Whole Campus Map", file: "/WHOLE CAMPUS MAP.png" }, // <--- NEW DEFAULT
  { name: "ARC Building", file: "/ARC Building.png" },
  { name: "COECSA Building", file: "/COECSA Building.png" },
  { name: "COECSA Annex", file: "/COECSA Annex Building.png" },
  { name: "JPL Building", file: "/JPL Building.png" },
  { name: "JPL East", file: "/JPL East Building.png" },
  { name: "Sotero Building", file: "/SOTERO Building.png" },
  { name: "Sotero West", file: "/SOTERO West Building.png" },
];

// --- MASTER LIST OF LOCATIONS ---
const allLocations = [
  { id: 'o13', name: 'Accounting Office', category: 'Office', icon: 'briefcase-outline' },
  { id: 'o10', name: 'Alumni and Media Relations', category: 'Office', icon: 'briefcase-outline' },
  { id: 'o4', name: 'Arts and Cultural Affairs', category: 'Office', icon: 'briefcase-outline' },
  { id: 'o3', name: 'Center for Student Affairs', category: 'Office', icon: 'briefcase-outline' },
  { id: 'o11', name: 'Communications and Public Affairs Department', category: 'Office', icon: 'briefcase-outline' },
  { id: 'o9', name: 'ETEEAP', category: 'Office', icon: 'briefcase-outline' },
  { id: 'o14', name: 'Executive Offices', category: 'Office', icon: 'briefcase-outline' },
  { id: 'o1', name: 'Guidance and Testing Center', category: 'Office', icon: 'briefcase-outline' },
  { id: 'o16', name: 'Health Services Department', category: 'Office', icon: 'briefcase-outline' },
  { id: 'o5', name: 'Internal Auditor', category: 'Office', icon: 'briefcase-outline' },
  { id: 'o7', name: 'Materials Management Office', category: 'Office', icon: 'briefcase-outline' },
  { id: 'o2', name: 'Office of Data Privacy', category: 'Office', icon: 'briefcase-outline' },
  { id: 'o8', name: 'Office of the Legal Aid', category: 'Office', icon: 'briefcase-outline' },
  { id: 'o6', name: 'Purchasing Office', category: 'Office', icon: 'briefcase-outline' },
  { id: 'o12', name: 'Registrar’s Office', category: 'Office', icon: 'briefcase-outline' },
  { id: 'o15', name: 'Security Office (Main)', category: 'Office', icon: 'briefcase-outline' },
  // ... (rest of your list is preserved)
].sort((a, b) => a.name.localeCompare(b.name));

// Helper function for icons
const getIconForCategory = (category: string) => {
  switch (category) {
    case 'Office': return '🖥️';
    case 'Laboratory': return '🧪';
    case 'Amenity': return '☕';
    case 'Library': return '📚';
    case 'Classroom': return '🏫';
    default: return '📍';
  }
};

export default function ManagePOIs() {
  // State defaults to the first item in the list (Whole Campus Map)
  const [selectedMap, setSelectedMap] = useState(campusMaps[0].file);
  
  const recentLocations = allLocations.slice(0, 5);

  return (
    <div className="manage-pois-container">
      
      {/* LEFT COLUMN: Controls */}
      <div className="controls-column">
        <h1>Manage Points of Interest (POIs)</h1>
        
        <div className="admin-welcome-card">
          <div className="welcome-text">
            <h2>Welcome, JOHN DOE!</h2>
            <p>Sunday, March 17, 2024</p>
          </div>
        </div>

        <p className="instruction-text">What would you like to do?</p>

        <div className="action-buttons">
          <button className="action-btn add-btn">
            <FaPlus /> Add New Location
          </button>
          <button className="action-btn remove-btn">
            <FaMinus /> Remove Location
          </button>
        </div>

        {/* Recent Locations List */}
        <div className="recent-list-container">
          <h3>Recently Added / Updated Locations</h3>
          <ul className="recent-list">
            {recentLocations.map((loc) => (
              <li key={loc.id} className="recent-item">
                <span className="loc-icon">{getIconForCategory(loc.category)}</span>
                <span className="loc-name">{loc.name}</span>
                <button className="edit-btn"><FaEdit /> Edit</button>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* RIGHT COLUMN: The Map Viewer */}
      <div className="map-column">
        
        {/* Map Selector Bar */}
        <div className="map-selector-bar">
          <FaMap className="map-icon" />
          <select 
            className="map-dropdown"
            onChange={(e) => setSelectedMap(e.target.value)}
            value={selectedMap}
          >
            {campusMaps.map((map) => (
              <option key={map.name} value={map.file}>
                {map.name}
              </option>
            ))}
          </select>
        </div>

        {/* The Selected Map Image */}
        <div className="map-image-wrapper">
          <img 
            src={selectedMap} 
            alt="Campus Map" 
            className="static-map-image"
          />
        </div>
      </div>

    </div>
  );
}