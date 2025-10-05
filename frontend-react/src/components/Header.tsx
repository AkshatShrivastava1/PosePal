import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Header.css';

const Header: React.FC = () => {
  const location = useLocation();

  return (
    <header className="top-nav">
      <div className="logo">
        <img src="/assets/PosePal.png" alt="PosePal Logo" />
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
      <div className="profile">
        <img src="/assets/profile.jpg" alt="User Profile" className="profile-pic" />
        <div className="profile-info">
          <span>Jose Simmons</span>
          <small>User</small>
        </div>
        <div className="profile-actions">
          <i className="fa-solid fa-gear"></i>
          <i className="fa-solid fa-ellipsis-vertical"></i>
        </div>
      </div>
    </header>
  );
};

export default Header;
