import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faImage, faEdit, faUserCircle, faSignOutAlt } from '@fortawesome/free-solid-svg-icons';
import { useNavigate } from 'react-router-dom';

import '../css/Sidebar.css';

function Sidebar({ onMenuClick }) {
  const navigate = useNavigate();
  const [activeMenu, setActiveMenu] = useState('closest-lots');

  const handleLogout = () => {
    // Clear the authentication token
    localStorage.removeItem('token');
    // Redirect to login page
    navigate('/');
  };

  return (
    <aside className="sidebar">
    <div className="login-area">
      <FontAwesomeIcon icon={faUserCircle} className="avatar"/>
      <div className="user-info">
        <p className="user-name">Janet Williams</p>
      </div>
    </div>
    <ul className="menu">
      <li 
        className={`menu-item ${activeMenu === 'closest-lots' ? 'active' : ''}`} 
        onClick={() => { setActiveMenu('closest-lots'); onMenuClick('closest-lots'); }}
      >
        <FontAwesomeIcon icon={faImage} className="menu-icon" />
        Closest Lots
      </li>
      <li 
        className={`menu-item ${activeMenu === 'optimize-sale' ? 'active' : ''}`} 
        onClick={() => { setActiveMenu('optimize-sale'); onMenuClick('optimize-sale'); }}
      >
        <FontAwesomeIcon icon={faEdit} className="menu-icon" />
        Optimize Your Sale
      </li>
      <li 
        className={`menu-item ${activeMenu === 'authentify-art' ? 'active' : ''}`} 
        onClick={() => { setActiveMenu('authentify-art'); onMenuClick('authentify-art'); }}
      >
        <FontAwesomeIcon icon={faEdit} className="menu-icon" />
        Authentify Your Art Piece
      </li>
    </ul>
    <button onClick={handleLogout} className="logout-button">
        <FontAwesomeIcon icon={faSignOutAlt} /> Logout
      </button>
  </aside>
  );
}

export default Sidebar;