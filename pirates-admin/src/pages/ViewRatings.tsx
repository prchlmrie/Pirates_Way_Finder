import { useState } from 'react';
import { FaChevronDown, FaChevronUp, FaSearch, FaUserCircle } from 'react-icons/fa';
import { MdSentimentNeutral, MdSentimentVeryDissatisfied, MdSentimentVerySatisfied } from 'react-icons/md';
import './ViewRatings.css';

// --- MASTER LIST OF LOCATIONS (Synced with Mobile App) ---
const allLocations = [
  // Offices
  { id: 'o13', name: 'Accounting Office', category: 'Office' },
  { id: 'o10', name: 'Alumni and Media Relations', category: 'Office' },
  { id: 'o4', name: 'Arts and Cultural Affairs', category: 'Office' },
  { id: 'o3', name: 'Center for Student Affairs', category: 'Office' },
  { id: 'o11', name: 'Communications and Public Affairs Department', category: 'Office' },
  { id: 'o9', name: 'ETEEAP', category: 'Office' },
  { id: 'o14', name: 'Executive Offices', category: 'Office' },
  { id: 'o1', name: 'Guidance and Testing Center', category: 'Office' },
  { id: 'o16', name: 'Health Services Department', category: 'Office' },
  { id: 'o5', name: 'Internal Auditor', category: 'Office' },
  { id: 'o7', name: 'Materials Management Office', category: 'Office' },
  { id: 'o2', name: 'Office of Data Privacy', category: 'Office' },
  { id: 'o8', name: 'Office of the Legal Aid', category: 'Office' },
  { id: 'o6', name: 'Purchasing Office', category: 'Office' },
  { id: 'o12', name: 'Registrar’s Office', category: 'Office' },
  { id: 'o15', name: 'Security Office (Main)', category: 'Office' },

  // Amenities
  { id: 'a2', name: 'ATM Machine (BDO ATM Only)', category: 'Amenity' },
  { id: 'a12', name: 'ATM Machines', category: 'Amenity' },
  { id: 'a13', name: 'Audio Visual Theatre (AVT)', category: 'Amenity' },
  { id: 'a14', name: 'Bookstore', category: 'Amenity' },
  { id: 'a15', name: 'Chapel of the Sacred Heart of Jesus', category: 'Amenity' },
  { id: 'a4', name: 'COECSA Lobby / Student Lounge', category: 'Amenity' },
  { id: 'a20', name: 'Comfort Room (JPL)', category: 'Amenity' },
  { id: 'a11', name: 'Comfort Room (Sotero)', category: 'Amenity' },
  { id: 'a17', name: 'Elevator', category: 'Amenity' },
  { id: 'a10', name: 'Le Café', category: 'Amenity' },
  { id: 'a7', name: 'Lemongrass Studio', category: 'Amenity' },
  { id: 'a5', name: 'Mahogany', category: 'Amenity' },
  { id: 'a18', name: 'Main Lobby', category: 'Amenity' },
  { id: 'a6', name: 'PPFM', category: 'Amenity' },
  { id: 'a8', name: 'Sotero Canteen / LPU-C Food Court', category: 'Amenity' },
  { id: 'a16', name: 'Student Center', category: 'Amenity' },
  { id: 'a3', name: 'The Circuit', category: 'Amenity' },
  { id: 'a1', name: 'The Forum', category: 'Amenity' },
  { id: 'a9', name: 'University Auditorium', category: 'Amenity' },
  { id: 'a19', name: 'VIP Entry', category: 'Amenity' },

  // Laboratories
  { id: 'l3', name: 'Culinary Laboratory 1', category: 'Laboratory' },
  { id: 'l1', name: 'Culinary Laboratory 2', category: 'Laboratory' },
  { id: 'l2', name: 'Demonstration Kitchen Laboratory', category: 'Laboratory' },

  // Libraries
  { id: 'lib1', name: 'E-Library', category: 'Library' },
  { id: 'lib2', name: 'Periodicals/Thesis Section', category: 'Library' },

  // Classrooms
  { id: 'c1', name: 'Thesis Defense Room', category: 'Classroom' },
].sort((a, b) => a.name.localeCompare(b.name));


// --- UPDATED MOCK DATA: Anonymous Users ---
const mockReviews = [
  { id: 3, user: 'Anonymous 003', rating: 'BAD', comment: 'The aircon was not working properly.', date: 'Mar 15, 2024' },
  { id: 2, user: 'Anonymous 002', rating: 'NOT BAD', comment: 'Queue was a bit long but service was okay.', date: 'Mar 14, 2024' },
  { id: 1, user: 'Anonymous 001', rating: 'GOOD', comment: 'Very helpful staff!', date: 'Mar 10, 2024' },
];

// Helper to get the right icon/color for a rating
const getRatingBadge = (rating: string) => {
  switch (rating) {
    case 'GOOD': return <span className="badge good"><MdSentimentVerySatisfied /> GOOD</span>;
    case 'NOT BAD': return <span className="badge not-bad"><MdSentimentNeutral /> NOT BAD</span>;
    case 'BAD': return <span className="badge bad"><MdSentimentVeryDissatisfied /> BAD</span>;
    default: return null;
  }
};

export default function ViewRatings() {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState(''); // NEW: Search State

  const toggleExpand = (id: string) => {
    if (expandedId === id) {
      setExpandedId(null);
    } else {
      setExpandedId(id);
    }
  };

  // NEW: Filter the locations based on search
  const filteredLocations = allLocations.filter(loc => 
    loc.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    loc.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="ratings-container">
      <h1>View User Ratings</h1>

      {/* --- NEW SEARCH BAR --- */}
      <div className="search-bar-container">
        <FaSearch className="search-icon" />
        <input 
          type="text" 
          placeholder="Search for an office, facility, or category..." 
          className="search-input"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <div className="locations-list">
        {filteredLocations.length > 0 ? (
          filteredLocations.map((loc) => {
            const isExpanded = expandedId === loc.id;

            return (
              <div key={loc.id} className={`location-card ${isExpanded ? 'expanded' : ''}`}>
                
                {/* The Clickable Header (Drop Bar) */}
                <div className="location-header" onClick={() => toggleExpand(loc.id)}>
                  <div className="location-info">
                    <span className={`category-tag ${loc.category.toLowerCase()}`}>{loc.category}</span>
                    <span className="location-name">{loc.name}</span>
                  </div>
                  <div className="header-right">
                    <span className="review-count">{isExpanded ? '3 Reviews' : 'View Reviews'}</span>
                    <span className="chevron">{isExpanded ? <FaChevronUp /> : <FaChevronDown />}</span>
                  </div>
                </div>

                {/* The Expanded Content (Reviews) */}
                {isExpanded && (
                  <div className="reviews-section">
                    {mockReviews.map((review) => (
                      <div key={review.id} className="review-item">
                        <div className="review-header">
                          <div className="user-info">
                            <FaUserCircle className="user-icon" />
                            <span className="username">{review.user}</span>
                          </div>
                          <span className="review-date">{review.date}</span>
                        </div>
                        
                        <div className="review-body">
                          {getRatingBadge(review.rating)}
                          <p className="review-comment">{review.comment}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })
        ) : (
          <p className="no-results">No locations found matching "{searchQuery}"</p>
        )}
      </div>
    </div>
  );
}