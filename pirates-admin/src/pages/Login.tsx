import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Login.css';

export default function Login() {
  const navigate = useNavigate();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    // In a real app, validate credentials here
    navigate('/dashboard');
  };

  return (
    <div className="login-container">
      <div className="login-overlay">
        
        {/* Header Logo */}
        <div className="login-header">
          <img src="/pirate-pin-logo.png" alt="Logo" />
          <h2>Pirates Way Finder</h2>
        </div>

        {/* Login Card */}
        <div className="login-card">
          <h3>Welcome Back!</h3>
          <p>We missed you! Please enter your details</p>

          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label>Email</label>
              <input type="email" placeholder="Enter your Email" required />
            </div>

            <div className="form-group">
              <label>Password</label>
              <input type="password" placeholder="Enter your Password" required />
            </div>

            <button type="submit" className="login-btn">Sign In</button>
            
            <a href="#" className="forgot-password">Forgot password?</a>
            <div style={{ marginTop: '20px', fontSize: '13px', color: '#666' }}>
              Don't have an account? 
              <Link to="/signup" style={{ color: '#8B0000', fontWeight: 'bold', marginLeft: '5px', textDecoration: 'none' }}>
                Create one
              </Link>
            </div>
          </form>
        </div>

        {/* Winding Path */}
        <img src="/winding-path.png" alt="Path" className="login-path" />
      </div>
    </div>
  );
}