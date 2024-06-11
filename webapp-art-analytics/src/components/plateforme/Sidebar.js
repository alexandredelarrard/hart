import React, { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faImage, faEdit, faUserCircle, faSignOutAlt } from '@fortawesome/free-solid-svg-icons';
import { useNavigate } from 'react-router-dom';
import Cookies from 'js-cookie';

import '../../css/Sidebar.css';

function Sidebar({ onMenuClick }) {
  const navigate = useNavigate();
  const [activeMenu, setActiveMenu] = useState('closest-lots');
  const [userData, setUserData] = useState({});

  const handleLogout = () => {
    // Clear the authentication token
    Cookies.remove('token');
    Cookies.remove('userdata');
    navigate('/');
  };

  useEffect(() => {
    const userdataCookie = Cookies.get('userdata');
    console.log(userdataCookie)
    if (userdataCookie) {
      try {
        const parsedUserdata = JSON.parse(userdataCookie);
        setUserData(parsedUserdata);
      } catch (error) {
        console.error('Failed to parse userdata cookie:', error);
      }
    }
  }, []);

  return (
    <aside className="sidebar">
    <div className="login-area">
      <FontAwesomeIcon icon={faUserCircle} className="avatar"/>
      <div className="user-info">
        <p className="user-name">{userData.name || 'User'}</p>
      </div>
    </div>
    <ul className="menu">
      <li 
          className={`menu-item ${activeMenu === 'search-art' ? 'active' : ''}`} 
          onClick={() => { setActiveMenu('search-art'); onMenuClick('search-art'); }}
        >
        <FontAwesomeIcon icon={faImage} className="menu-icon" />
        Search Art piece
      </li>
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