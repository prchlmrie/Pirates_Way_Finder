import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Signup.css';

export default function Signup() {
  const navigate = useNavigate();

  const handleSignup = (e: React.FormEvent) => {
    e.preventDefault();
    // In a real app, you would send data to backend here
    alert("Account created successfully!");
    navigate('/dashboard');
  };

  return (
    <div className="signup-container">
      <div className="signup-overlay"></div>
      
      {/* Reusing the path image for consistency */}
      <img src="/winding-path.png" alt="Path" className="signup-path" />

      <div className="signup-content">
        <div className="signup-header">
          <img src="/pirate-pin-logo.png" alt="Logo" />
          <h2>Pirates Way Finder</h2>
        </div>

        <div className="signup-card">
          <h3>Create Account</h3>
          <p>Join the crew! Please fill in your details.</p>

          <form onSubmit={handleSignup}>
            <div className="form-group">
              <label>Full Name</label>
              <input type="text" placeholder="John Doe" required />
            </div>

            <div className="form-group">
              <label>Email</label>
              <input type="email" placeholder="admin@lpu.edu.ph" required />
            </div>

            <div className="form-group">
              <label>Password</label>
              <input type="password" placeholder="Create a password" required />
            </div>

            <div className="form-group">
              <label>Confirm Password</label>
              <input type="password" placeholder="Confirm your password" required />
            </div>

            <button type="submit" className="signup-btn">Sign Up</button>
            
            <div className="login-link">
              Already have an account? <Link to="/login">Sign In</Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}