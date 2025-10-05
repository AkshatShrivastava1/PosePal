import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { AuthService } from '../services/authService';
import './Header.css';

const Header: React.FC = () => {
  const location = useLocation();
  const isAuthenticated = AuthService.isAuthenticated();

  const handleLogout = () => {
    AuthService.removeToken();
    window.location.href = '/';
  };

  return (
    <header className="top-nav">
      <div className="logo">
        <div className="logo-placeholder">
          <i className="fa-solid fa-dumbbell"></i>
          <span>PosePal</span>
        </div>
      </div>
      <nav>
        <ul>
          <li className={location.pathname === '/about' ? 'active' : ''}>
            <Link to="/about">
              <i className="fa-solid fa-info-circle"></i> About Us
            </Link>
          </li>
          <li className={location.pathname === '/workout' ? 'active' : ''}>
            <Link to="/workout">
              <i className="fa-solid fa-running"></i> Get Moving
            </Link>
          </li>
        </ul>
      </nav>
      
      {isAuthenticated ? (
        <div className="profile">
          <img src="/assets/profile.jpg" alt="User Profile" className="profile-pic" />
          <div className="profile-info">
            <span>User</span>
            <small>Logged In</small>
          </div>
          <div className="profile-actions">
            <button onClick={handleLogout} className="logout-btn" title="Logout">
              <i className="fa-solid fa-sign-out-alt"></i>
            </button>
          </div>
        </div>
      ) : (
        <div className="auth-buttons">
          <Link to="/login" className="auth-btn login-btn">
            <i className="fa-solid fa-sign-in-alt"></i> Login
          </Link>
          <Link to="/signup" className="auth-btn signup-btn">
            <i className="fa-solid fa-user-plus"></i> Sign Up
          </Link>
        </div>
      )}
    </header>
  );
};

export default Header;
