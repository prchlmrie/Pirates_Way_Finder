import React, { useState } from 'react';
import { FaCheckCircle, FaPlus, FaTimesCircle, FaTrash, FaWheelchair } from 'react-icons/fa';
import { MdAccessible, MdElevator } from 'react-icons/md';
import './ManageAccessibility.css';

// --- INITIAL DATA ---
const initialBuildingData = {
  "COECSA": {
    name: "COECSA Building",
    mapImage: "/COECSA Building.png",
    features: [
      { id: 1, type: 'ramp', name: "COECSA Building Ramp", status: "Available" },
      { id: 2, type: 'elevator', name: "COECSA Elevator", status: "Under Maintenance" },
      { id: 3, type: 'restroom', name: "The Circuit PWD Restroom", status: "Available" },
    ]
  },
  "JPL": {
    name: "JPL Building",
    mapImage: "/JPL Building.png",
    features: [
      { id: 1, type: 'ramp', name: "JPL Building Ramp", status: "Available" },
      { id: 2, type: 'restroom', name: "JPL Ground Floor PWD Restroom", status: "Available" },
    ]
  },
  "SOTERO": {
    name: "Sotero Building",
    mapImage: "/SOTERO Building.png",
    features: [
      { id: 1, type: 'ramp', name: "Sotero Building Ramp", status: "Blocked" },
    ]
  },
  "ARC": {
    name: "ARC Building",
    mapImage: "/ARC Building.png",
    features: [
      { id: 1, type: 'ramp', name: "ARC Building Ramp", status: "Available" },
    ]
  }
};

// Helper to get icon based on feature type
const getFeatureIcon = (type: string) => {
  switch (type) {
    case 'ramp': return <FaWheelchair />;
    case 'elevator': return <MdElevator />;
    case 'restroom': return <MdAccessible />;
    default: return <FaCheckCircle />;
  }
};

export default function ManageAccessibility() {
  // 1. Store data in State so we can modify it
  const [buildings, setBuildings] = useState(initialBuildingData);
  const [selectedKey, setSelectedKey] = useState<keyof typeof initialBuildingData>("COECSA");
  
  // 2. State for the "Add New" form
  const [isAdding, setIsAdding] = useState(false);
  const [newFeatureName, setNewFeatureName] = useState("");
  const [newFeatureType, setNewFeatureType] = useState("ramp");
  const [newFeatureStatus, setNewFeatureStatus] = useState("Available");

  const currentBuilding = buildings[selectedKey];

  // --- DELETE FUNCTION ---
  const handleDelete = (id: number) => {
    if (!window.confirm("Are you sure you want to remove this accessibility feature?")) return;

    const updatedFeatures = currentBuilding.features.filter(f => f.id !== id);
    
    setBuildings({
      ...buildings,
      [selectedKey]: {
        ...currentBuilding,
        features: updatedFeatures
      }
    });
  };

  // --- ADD FUNCTION ---
  const handleAddFeature = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newFeatureName.trim()) return;

    const newId = Date.now(); // Simple ID generation
    const newFeature = {
      id: newId,
      type: newFeatureType,
      name: newFeatureName,
      status: newFeatureStatus
    };

    setBuildings({
      ...buildings,
      [selectedKey]: {
        ...currentBuilding,
        features: [...currentBuilding.features, newFeature]
      }
    });

    // Reset form
    setNewFeatureName("");
    setIsAdding(false);
  };

  // Mock function to toggle status
  const toggleStatus = (featureId: number) => {
    alert(`Toggled status for feature ID: ${featureId}`);
  };

  return (
    <div className="access-container">
      
      {/* --- LEFT COLUMN: Controls --- */}
      <div className="access-controls">
        <h1>Manage Accessibility</h1>
        {/* Building Selector */}
        <div className="selector-group">
          <label>Select Building:</label>
          <select 
            value={selectedKey} 
            onChange={(e) => setSelectedKey(e.target.value as keyof typeof initialBuildingData)}
            className="building-select"
          >
            {Object.entries(buildings).map(([key, data]) => (
              <option key={key} value={key}>{data.name}</option>
            ))}
          </select>
        </div>

        {/* Add New Feature Button */}
        {!isAdding ? (
          <button className="add-feature-btn" onClick={() => setIsAdding(true)}>
            <FaPlus /> Add Access Point
          </button>
        ) : (
          <form className="add-feature-form" onSubmit={handleAddFeature}>
            <h4>Add New Access Point</h4>
            <input 
              type="text" 
              placeholder="Feature Name (e.g., Main Ramp)" 
              value={newFeatureName}
              onChange={(e) => setNewFeatureName(e.target.value)}
              required
            />
            <div className="form-row">
              <select value={newFeatureType} onChange={(e) => setNewFeatureType(e.target.value)}>
                <option value="ramp">Ramp</option>
                <option value="elevator">Elevator</option>
                <option value="restroom">Restroom</option>
              </select>
              <select value={newFeatureStatus} onChange={(e) => setNewFeatureStatus(e.target.value)}>
                <option value="Available">Available</option>
                <option value="Under Maintenance">Maintenance</option>
                <option value="Blocked">Blocked</option>
              </select>
            </div>
            <div className="form-actions">
              <button type="button" className="cancel-btn" onClick={() => setIsAdding(false)}>Cancel</button>
              <button type="submit" className="save-btn">Save</button>
            </div>
          </form>
        )}

        {/* Accessibility Features List */}
        <div className="features-list">
          {currentBuilding.features.length === 0 ? (
            <p className="empty-msg">No accessibility features added yet.</p>
          ) : (
            currentBuilding.features.map((feature) => (
              <div key={feature.id} className={`feature-card ${feature.status === 'Available' ? 'active' : 'inactive'}`}>
                <div className="feature-icon-wrapper">
                  {getFeatureIcon(feature.type)}
                </div>
                
                <div className="feature-info">
                  <h4>{feature.name}</h4>
                  <span className={`status-badge ${feature.status.toLowerCase().replace(' ', '-')}`}>
                    {feature.status === 'Available' ? <FaCheckCircle /> : <FaTimesCircle />}
                    {feature.status}
                  </span>
                </div>

                <div className="card-actions">
                  <button className="toggle-btn-access" onClick={() => toggleStatus(feature.id)}>
                    Change Status
                  </button>
                  <button className="delete-btn" onClick={() => handleDelete(feature.id)} title="Remove">
                    <FaTrash />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* --- RIGHT COLUMN: Map Preview --- */}
      <div className="access-map-preview">
        <div className="map-header">
          <h3>{currentBuilding.name} Layout</h3>
          <span className="live-indicator">
             <span className="dot"></span> Live View
          </span>
        </div>
        <div className="image-wrapper">
          <img 
            src={currentBuilding.mapImage} 
            alt={currentBuilding.name} 
            className="building-map-img"
          />
        </div>
      </div>

    </div>
  );
}