import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { logout, checkAuth } from '../../utils/identification';
import { logActivity } from '../../utils/activity';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faImage, faEdit, faUserCircle, faSignOutAlt, faChevronRight, faChevronDown, faTrash } from '@fortawesome/free-solid-svg-icons';
import { useNavigate } from 'react-router-dom';
import { URL_API, URL_GET_TASK_RESULTS, URL_DELETE_TASK_RESULT } from '../../utils/constants';
import Cookies from 'js-cookie';

import '../../css/Sidebar.css';

function Sidebar({ 
  onMenuClick, 
  setFile,
  setText,
  setTaskId,
  setResult,
  setBotResult,
  setChatBotResultFetched,
  setAdditionalData,
  setAvgMaxEstimates,
  setAvgMinEstimates,
  newResultSaved,
  setAnalysisInProgress 
}) {
  const navigate = useNavigate();
  const [activeMenu, setActiveMenu] = useState('closest-lots');
  const [userData, setUserData] = useState({});
  const [formerResults, setFormerResults] = useState([]);
  const [showResults, setShowResults] = useState(false);

  const handleLogout = async () => {
    // log activity 
    logActivity("click_log_out", "")
    
    await logout();
    navigate('/login'); // Redirect to the login page or home page
  };

  useEffect(() => {
    const checkUserAuth = async () => {
      const isAuthenticated = await checkAuth();
      if (!isAuthenticated) {
        navigate('/login'); // Redirect to the login page or home page if not authenticated
      }
    };

    checkUserAuth();

    const interval = setInterval(checkUserAuth, 240000); // Check every 4 minute
    return () => clearInterval(interval);
  }, [navigate]);

  const toggleResults = (e) => {
    setShowResults(e);
  };

  const handleResultClick = (result) => {
    const byteCharacters = atob(result.file);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: 'image/jpg' });
    console.log(blob)

    setFile(blob);
    setText(result.text);
    setResult({
      distances: result.closest_distances.split(','),
      ids: result.closest_ids.split(',')
    });
    setTaskId(result.task_id);
    setAnalysisInProgress(true);
    setAdditionalData([]);
    setAvgMinEstimates(0);
    setAvgMaxEstimates(0);
    setBotResult(null)
    setChatBotResultFetched(false);
    onMenuClick('closest-lots');

    // log activity 
    logActivity("click_former_result", result.task_id)

  };

  const handleDeleteResult = (taskId) => {
    const confirmDelete = window.confirm(`Etes vous cetain de vouloir supprimer l'élément ${taskId}?`);
    if (confirmDelete) {
      axios.delete(`${URL_API + URL_DELETE_TASK_RESULT}/${taskId}`)
        .then(response => {
          // Remove the deleted result from the state
          setFormerResults(formerResults.filter(result => result.task_id !== taskId));
          // log activity 
          logActivity("delete_former_result", taskId)
        })
        .catch(error => {
          console.error('Error deleting the result:', error);
        });
    }
  };

  useEffect(() => {
    const userdataCookie = Cookies.get('userdata');
    if (userdataCookie) {
      try {
        const parsedUserdata = JSON.parse(userdataCookie);
        setUserData(parsedUserdata);

        axios.get(`${URL_API + URL_GET_TASK_RESULTS}?user_id=${parsedUserdata.id}`)
          .then(response => {
              setFormerResults(response.data.results); 
          })
          .catch(error => {
              console.error('Error fetching former results:', error);
          });

      } catch (error) {
        console.error('Failed to parse userdata cookie:', error);
      }
    }
  }, [newResultSaved]);

  const organizeResults = (results) => {
    const organizedResults = {
      "Today": [],
      "Yesterday": [],
      "Last Week": [],
      "Last Month": [],
      "Older": []
    };

    const now = new Date();
    results.forEach(result => {
      const resultDate = new Date(result.result_date);
      const differenceInDays = Math.floor((now - resultDate) / (1000 * 60 * 60 * 24));

      if (differenceInDays <= 1) {
        organizedResults["Today"].push(result);
      } else if (differenceInDays < 2) {
        organizedResults["Yesterday"].push(result);
      } else if (differenceInDays <= 7) {
        organizedResults["Last Week"].push(result);
      } else if (differenceInDays <= 30) {
        organizedResults["Last Month"].push(result);
      } else {
        organizedResults["Older"].push(result);
      }
    });

    // Remove keys with empty lists
    Object.keys(organizedResults).forEach(key => {
      if (organizedResults[key].length === 0) {
        delete organizedResults[key];
      }
    });

    return organizedResults;
  };

  const organizedResults = organizeResults(formerResults);

  return (
    <aside className="sidebar">
      <div className="login-area">
        <FontAwesomeIcon icon={faUserCircle} className="avatar"/>
        <div className="user-info">
          <p className="user-name">{userData.name || 'User'}</p>
          <p className="user-name">{userData.surname || 'User'}</p>
        </div>
      </div>
      <ul className="menu">
        <li 
          className={`menu-item ${activeMenu === 'search-art' ? 'active' : ''}`} 
          onClick={() => { setActiveMenu('search-art'); onMenuClick('search-art'); toggleResults(false); }}
        >
          <FontAwesomeIcon icon={faImage} className="menu-icon" />
          Search Art piece
        </li>
        <li 
          className={`menu-item ${activeMenu === 'closest-lots' ? 'active' : ''}`} 
          onClick={() => { setActiveMenu('closest-lots'); onMenuClick('closest-lots'); toggleResults(true); }}
        >
          <FontAwesomeIcon icon={faImage} className="menu-icon" />
          Closest Lots
          <FontAwesomeIcon icon={showResults ? faChevronDown : faChevronRight} className="submenu-icon" />
        </li>
        {showResults && (
          <div className="results-container">
            {Object.keys(organizedResults).map((category) => (
              <div key={category}>
                <h4 className="results-category">{category}</h4>
                <ul className="submenu">
                  {organizedResults[category].map((result, index) => (
                    <li 
                      key={index} 
                      className="submenu-item" 
                    >
                      <span onClick={() => handleResultClick(result)}>{result.task_id || `Result ${index + 1}`}</span>
                      <FontAwesomeIcon 
                        icon={faTrash} 
                        className="delete-icon" 
                        onClick={() => handleDeleteResult(result.task_id)}
                      />
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
        <li 
          className={`menu-item ${activeMenu === 'optimize-sale' ? 'active' : ''}`} 
          onClick={() => { setActiveMenu('optimize-sale'); onMenuClick('optimize-sale'); toggleResults(false); }}
        >
          <FontAwesomeIcon icon={faEdit} className="menu-icon" />
          Optimize Your Sale
        </li>
      </ul>
      <button onClick={handleLogout} className="logout-button">
        <FontAwesomeIcon icon={faSignOutAlt} /> Logout
      </button>
    </aside>
  );
}

export default Sidebar;