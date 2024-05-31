import React, { useState } from 'react';
import axios from 'axios';
import {URL_API_BACK, URL_UPLOAD} from '../utils/constants';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faImage, faEdit, faUserCircle, faSignOutAlt } from '@fortawesome/free-solid-svg-icons';
import { useNavigate } from 'react-router-dom';

import '../css/Sidebar.css';

function Sidebar({ onTaskSubmit }) {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [text, setText] = useState('');
  const [activeMenu, setActiveMenu] = useState('closest-lots');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleTextChange = (e) => {
    setText(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    if (file) {
      formData.append('file', file);
    }
    if (text) {
      formData.append('text', text);
    }
    
    try {
      const response = await axios.post(URL_API_BACK + URL_UPLOAD, formData,{
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      const task_id = response.data.task_id;
      console.log(task_id)
      onTaskSubmit(task_id, file, text);
    } catch (error) {
      console.error('Error uploading file', error);
    }
  };

  const handleLogout = () => {
    // Clear the authentication token
    localStorage.removeItem('token');
    // Redirect to login page
    navigate('/login');
  };

  return (
    <aside className="sidebar">
    <div className="login-area">
      <img src="/path/to/avatar.jpg" alt="Avatar" className="avatar" />
      <div className="user-info">
        <p className="user-name">Janet Williams</p>
      </div>
    </div>
    <ul className="menu">
      <li 
        className={`menu-item ${activeMenu === 'closest-lots' ? 'active' : ''}`} 
        onClick={() => setActiveMenu('closest-lots')}
      >
        <FontAwesomeIcon icon={faImage} className="menu-icon" />
        Closest Lots
      </li>
      {activeMenu === 'closest-lots' && (
        <form onSubmit={handleSubmit} className="sidebar-form">
          <div className="form-group">
            <input type="file" onChange={handleFileChange} className="input-file" />
          </div>
          <div className="form-group">
            <textarea
              value={text}
              onChange={handleTextChange}
              placeholder="Enter text"
              className="textarea"
            />
          </div>
          <button type="submit" className="send-button">Send for Analysis</button>
        </form>
      )}
      <li 
        className={`menu-item ${activeMenu === 'optimize-sale' ? 'active' : ''}`} 
        onClick={() => setActiveMenu('optimize-sale')}
      >
        <FontAwesomeIcon icon={faEdit} className="menu-icon" />
        Optimize Your Sale
      </li>
      <li 
        className={`menu-item ${activeMenu === 'authentify-art' ? 'active' : ''}`} 
        onClick={() => setActiveMenu('authentify-art')}
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