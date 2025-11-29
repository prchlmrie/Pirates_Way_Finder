import { useState } from 'react';
import { Navigate, Route, BrowserRouter as Router, Routes, useLocation } from 'react-router-dom';

// --- Components ---
import Sidebar from './components/Sidebar';

// --- Pages ---
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import ManageAccessibility from './pages/ManageAccessibility';
import ManagePOIs from './pages/ManagePOIs';
import Signup from './pages/Signup';
import ViewRatings from './pages/ViewRatings';
import Welcome from './pages/Welcome';

function Layout() {
  const location = useLocation();
  
  // Define public pages where the sidebar should NOT show
  const isPublicPage = ['/', '/login', '/signup'].includes(location.pathname);

  // State for sidebar collapse
  const [isCollapsed, setIsCollapsed] = useState(false);
  const toggleSidebar = () => setIsCollapsed(!isCollapsed);

  // 1. Render Public Pages (No Sidebar)
  if (isPublicPage) {
    return (
      <Routes>
        <Route path="/" element={<Welcome />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        {/* Redirect unknown public routes to Welcome */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    );
  }

  // 2. Render Admin Layout (With Sidebar)
  return (
    <div className="app-container">
      <Sidebar isCollapsed={isCollapsed} toggleSidebar={toggleSidebar} />
      
      <div className={`main-content ${isCollapsed ? 'collapsed' : ''}`}>
        <Routes>
          {/* Dashboard */}
          <Route path="/dashboard" element={<Dashboard />} />
          
          {/* Map Editor */}
          <Route path="/manage-pois" element={<ManagePOIs />} />
          
          {/* Accessibility Manager */}
          <Route path="/accessibility" element={<ManageAccessibility />} />

          {/* Ratings Viewer */}
          <Route path="/ratings" element={<ViewRatings />} />
          
          {/* Redirect unknown admin routes to Dashboard */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Layout />
    </Router>
  );
}

export default App;