import { useNavigate } from 'react-router-dom';
import './Welcome.css';

export default function Welcome() {
  const navigate = useNavigate();

  return (
    <div className="welcome-container">
      <div className="welcome-overlay">
        
        <div className="welcome-logo-container">
          {/* Combine hat and pin if you have them separately, or use the combined logo */}
          <img src="/pirate-pin-logo.png" alt="Logo" className="welcome-logo" />
        </div>

        <h1 className="welcome-title">Pirates Way Finder</h1>

        <button 
          className="get-started-btn"
          onClick={() => navigate('/login')}
        >
          Get Started
        </button>

        {/* The Winding Path Image at the bottom */}
        <img src="/winding-path.png" alt="Path" className="winding-path" />
      </div>
    </div>
  );
}