import React, { useState } from 'react';
import axios from 'axios';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faImage, faEdit, faUserCircle, faSignOutAlt, faChevronRight, faChevronDown, faTrash } from '@fortawesome/free-solid-svg-icons';
import { useTranslation } from 'react-i18next';
import Cookies from 'js-cookie';

import {organizeResults} from './upload_utils/organizeSidebar.js';
import { URL_API, URL_DELETE_TASK_RESULT } from '../../utils/constants';

import { logout } from '../../hooks/general/identification';
import useLogActivity from '../../hooks/general/useLogActivity.js';
import useFetchPastResults from '../../hooks/plateforme/useFetchPastResults.js';

import '../../css/Sidebar.css';

function Sidebar({ 
  userData,
  setUserData,
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
  setAnalysisInProgress,
  newResultSaved,
  setMinPrice,
  setMaxPrice,
  setMinDate,
  setMaxDate,
  t
}) {
  const [activeMenu, setActiveMenu] = useState('search-art');
  const [formerResults, setFormerResults] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const { i18n } = useTranslation('/analytics');
  const LogActivity = useLogActivity();

  //logout on click button
  const handleLogout = async () => {

    // log activity 
    const success = await LogActivity("click_log_out", "")
    if (success) {
      console.log('Activity logged successfully');
    } else {
      console.log('Failed to log activity');
    }

    setResult(null);
    setText('');
    setFile(null);
    setAdditionalData([]);
    setBotResult(null);
    setMinPrice('');
    setMaxPrice('');
    setMinDate('');
    setMaxDate('');
    
    await logout();
  };

  const toggleResults = (e) => {
    if(e===true&&showResults===true){setShowResults(false);}
    else{setShowResults(e);}
  };

  const handleResultClick = (result) => {
    const byteCharacters = atob(result.file);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: 'image/jpg' });
    
    setFile(blob);
    setText(result.text);
    setResult({
      distances: result.closest_distances.split(','),
      ids: result.closest_ids.split(',')
    });
    setTaskId(result.task_id);
    setAnalysisInProgress(false);
    setAdditionalData([]);
    setAvgMinEstimates(0);
    setAvgMaxEstimates(0);
    setMinPrice('');
    setMaxPrice('');
    setMinDate('');
    setMaxDate('');
    if(result.llm_result){
      const llm_result = JSON.parse(JSON.stringify(result.llm_result));
      setBotResult(llm_result)
      setChatBotResultFetched(true);
    } else {
      setBotResult(null)
      setChatBotResultFetched(false);
    }

    // menu is clicked 
    onMenuClick('closest-lots');

    // log activity 
    LogActivity("click_former_result", result.task_id)

  };

  const handleDeleteResult = (taskId, title) => {
    const token = Cookies.get('token');
    const confirmDelete = window.confirm(`${t("plateforme.sidebar.deleteconfirm")} \n ${title || taskId}?`);
    if (confirmDelete) {
      axios.delete(`${URL_API + URL_DELETE_TASK_RESULT}/${taskId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )
        .then(response => {
          // Remove the deleted result from the state
          setFormerResults(formerResults.filter(result => result.task_id !== taskId));
          // log activity 
          LogActivity("delete_former_result", taskId)
        })
        .catch(error => {
          console.error('Error deleting the result:', error);
        });
    }
  };

  // retrieve past results
  useFetchPastResults(newResultSaved, setFormerResults, setUserData);
  const organizedResults = organizeResults(formerResults, t);

  return (
    <aside className="sidebar">
      <div className="login-area">
        <FontAwesomeIcon icon={faUserCircle} className="sidebar-avatar"/>
        <div className="user-info">
          <p className="user-name">{userData.name || t("plateforme.sidebar.defaultusername")}</p>
          <p className="user-name">{userData.surname || t("plateforme.sidebar.defaultusername")}</p>
        </div>
      </div>
      <ul className="menu">
        <li 
          className={`menu-item ${activeMenu === 'search-art' ? 'active' : ''}`} 
          onClick={() => { setActiveMenu('search-art'); onMenuClick('search-art'); toggleResults(false); }}
        >
          <FontAwesomeIcon icon={faImage} className="menu-icon" />
          {t("plateforme.sidebar.search")}
        </li>
        <li 
          className={`menu-item ${activeMenu === 'closest-lots' ? 'active' : ''}`} 
          onClick={() => { setActiveMenu('closest-lots'); onMenuClick('closest-lots'); toggleResults(true); }}
        >
          <FontAwesomeIcon icon={faImage} className="menu-icon" />
          {t("plateforme.sidebar.closest")}
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
                      onClick={() => handleResultClick(result)}
                    >
                      <span>
                          {result.llm_result ? (
                            i18n.language === "fr" ? (
                              result.llm_result.french_title || result.taskId
                            ) : (
                              result.llm_result.english_title || result.taskId
                            )
                          ) : (
                            result.taskId
                          )}
                        </span>
                      <FontAwesomeIcon 
                        icon={faTrash} 
                        className="delete-icon" 
                        onClick={() => handleDeleteResult(result.task_id, result.llm_result ? (
                          i18n.language === "fr" ? (
                            result.llm_result.french_title || result.task_id
                          ) : (
                            result.llm_result.english_title || result.task_id
                          )
                        ) : (
                          result.task_id
                        ))}
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
          {t("plateforme.sidebar.optimize")}
        </li>
      </ul>
      <button onClick={handleLogout} className="logout-button">
        <FontAwesomeIcon icon={faSignOutAlt} />{t("plateforme.sidebar.logout")}
      </button>
    </aside>
  );
}

export default Sidebar;