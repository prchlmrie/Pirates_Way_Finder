import './Dashboard.css';

export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      
      <div className="dashboard-grid">
        
        {/* 1. Welcome Banner */}
        <div className="welcome-banner area-welcome">
          <div>
            <h2>Welcome, JOHN DOE!</h2>
            <p>Sunday, March 17, 2024</p>
          </div>
          <div className="pirate-mascot-container">
             <img 
               src="/pirate-logo.png" 
               alt="Pirate Mascot" 
               className="dashboard-mascot-img" 
             />
          </div>
        </div>

        {/* 2. Notifications Panel */}
        <div className="notifications-panel area-notif">
          <h3>🔔 Notifications</h3>
          <ul className="notif-list">
             <li className="notif-item">⭐ You have received one rating</li>
             <li className="notif-item">⭐ You have received one rating</li>
             <li className="notif-item success">✅ Pathway successfully added</li>
          </ul>
        </div>

        {/* 3. Stats Cards */}
        <div className="stat-card area-stat1">
          <div className="stat-icon-container">📍</div>
          <h3>Total Points of Interest (POIs)</h3>
          <div className="stat-number">130 <span>POIs</span></div>
        </div>

        <div className="stat-card area-stat2">
          <div className="stat-icon-container">🗺️</div>
          <h3>Total Accessibility Routes</h3>
          <div className="stat-number">200 <span>routes</span></div>
        </div>

        <div className="stat-card area-stat3">
          <div className="stat-icon-container">⭐</div>
          <h3>Total user ratings</h3>
          <div className="stat-number">67 <span>ratings</span></div>
        </div>

      </div>
    </div>
  );
}