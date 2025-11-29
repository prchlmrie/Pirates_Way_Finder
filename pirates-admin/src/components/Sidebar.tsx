import { FaBars, FaChartPie, FaMapMarkedAlt, FaRoute, FaSignOutAlt, FaStar } from 'react-icons/fa';
import { Link, useLocation } from 'react-router-dom';
import './Sidebar.css';

interface SidebarProps {
  isCollapsed: boolean;
  toggleSidebar: () => void;
}

export default function Sidebar({ isCollapsed, toggleSidebar }: SidebarProps) {
  const location = useLocation();

  const menuItems = [
    // Using FaChartPie here requires importing it above
    { path: '/dashboard', name: 'Dashboard', icon: <FaChartPie /> }, 
    { path: '/manage-pois', name: 'Manage POIs', icon: <FaMapMarkedAlt /> },
    { path: '/accessibility', name: 'Manage Accessibility', icon: <FaRoute /> },
    { path: '/ratings', name: 'View User Ratings', icon: <FaStar /> },
  ];

  return (
    <div className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        {/* Area 1: Toggle Button */}
        <div className="toggle-container">
          <button className="toggle-btn" onClick={toggleSidebar}>
            <FaBars />
          </button>
        </div>
        
        {/* Area 2: Brand (Logo + Text) */}
        <div className="brand-container">
           <img 
            src="/pirate-pin-logo.png" 
            alt="Logo" 
            className="sidebar-logo-img"
          />
          <div className="brand-text">
            <h2>Pirates<br/>Way Finder</h2>
          </div>
        </div>
      </div>

      <nav className="sidebar-menu">
        {menuItems.map((item) => (
          <Link 
            key={item.path} 
            to={item.path}
            className={`menu-item ${location.pathname === item.path ? 'active' : ''}`}
            title={isCollapsed ? item.name : ''}
          >
            <span className="icon">{item.icon}</span>
            {!isCollapsed && <span className="label">{item.name}</span>}
          </Link>
        ))}
      </nav>

      <div className="sidebar-footer">
        <button className="logout-btn">
          <FaSignOutAlt /> 
          {!isCollapsed && <span>Log Out</span>}
        </button>
      </div>
    </div>
  );
}