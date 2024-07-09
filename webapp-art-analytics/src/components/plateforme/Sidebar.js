import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faImage, faEdit, faUserCircle, faSignOutAlt, faChevronRight, faChevronDown, faTrash } from '@fortawesome/free-solid-svg-icons';
import { useTranslation } from 'react-i18next';
import Cookies from 'js-cookie';

import { organizeResults } from './upload_utils/organizeSidebar.js';
import { URL_API, URL_DELETE_TASK_RESULT } from '../../utils/constants';

import { logout, checkAuth } from '../../hooks/general/identification';
import useLogActivity from '../../hooks/general/useLogActivity.js';
import FetchPastResults from '../../hooks/plateforme/FetchPastResults.js';


import '../../css/Sidebar.css';

function Sidebar({
  userData,
  setUserData,
  onMenuClick,
  uploadFormHandlers,
  uploadFormState,
  t
}) {
  const {
    analysisInProgress,
    newResultSaved,
    chatBotResultFetched
  } = uploadFormState;

  const [formerResults, setFormerResults] = useState([]);
  const [activeMenu, setActiveMenu] = useState('search-art');
  const [activeLi, setActiveLi] = useState('');
  const [clickResult, setClickResult] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const { i18n } = useTranslation('/analytics');
  const LogActivity = useLogActivity();

  // Logout on click button
  const handleLogout = async () => {
    const success = await LogActivity("click_log_out", "");
    if (success) {
      console.log('Activity logged successfully');
    } else {
      console.log('Failed to log activity');
    }

    uploadFormHandlers.setResult(null);
    uploadFormHandlers.setText('');
    uploadFormHandlers.setFile(null);
    uploadFormHandlers.setAdditionalData([]);
    uploadFormHandlers.setBotResult(null);
    uploadFormHandlers.setMinPrice('');
    uploadFormHandlers.setMaxPrice('');
    uploadFormHandlers.setMinDate('');
    uploadFormHandlers.setMaxDate('');

    await logout();
  };

  const toggleResults = (e) => {
    if (e === true && showResults === true) {
      setShowResults(false);
    } else {
      setShowResults(e);
    }
  };

  const handleResultClick = (result) => {
    setClickResult(!clickResult);

    const byteCharacters = atob(result.file);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: 'image/jpg' });

    uploadFormHandlers.setFile(blob);
    uploadFormHandlers.setText(result.text);
    uploadFormHandlers.setResult({ answer: result.answer });
    uploadFormHandlers.setTaskId(result.task_id);
    uploadFormHandlers.setAnalysisInProgress(false);
    uploadFormHandlers.setAdditionalData([]);
    uploadFormHandlers.setAvgMinEstimates(null);
    uploadFormHandlers.setAvgMaxEstimates(null);
    uploadFormHandlers.setAvgFinalResult(null);
    uploadFormHandlers.setMinPrice('');
    uploadFormHandlers.setMaxPrice('');
    uploadFormHandlers.setMinDate('');
    uploadFormHandlers.setMaxDate('');
    if (result.llm_result) {
      const llm_result = JSON.parse(JSON.stringify(result.llm_result));
      uploadFormHandlers.setBotResult(llm_result);
      uploadFormHandlers.setChatBotResultFetched(true);
    } else {
      uploadFormHandlers.setBotResult(null);
      uploadFormHandlers.setChatBotResultFetched(false);
    }

    // onMenuClick('closest-lots');
    LogActivity("click_former_result", result.task_id);
  };

  const handleDeleteResult = (taskId, title) => {
    const token = Cookies.get('token');
    const confirmDelete = window.confirm(`${t("plateforme.sidebar.deleteconfirm")} \n ${title || taskId}?`);
    if (confirmDelete) {
      axios.delete(`${URL_API + URL_DELETE_TASK_RESULT}/${taskId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
        .then(response => {
          setFormerResults(formerResults.filter(result => result.task_id !== taskId));
          LogActivity("delete_former_result", taskId);
        })
        .catch(error => {
          console.error('Error deleting the result:', error);
        });
    }
  };

  useEffect(() => {
    const isAuthenticated = checkAuth();
    const userdataCookie = Cookies.get('userdata');

      if (isAuthenticated) {
        if (userdataCookie) {
            const parsedUserdata = JSON.parse(userdataCookie);
            setUserData(parsedUserdata);
        }
      }

  }, [setUserData]);

  useEffect(() => {
    if (!chatBotResultFetched) {
      // Function to call FetchResult every 5 seconds for 1 minute
      const interval = setInterval(() => FetchPastResults(setFormerResults), 5000);
      const timeout = setTimeout(() => clearInterval(interval), 180000);

      // Cleanup function to clear interval and timeout if the component unmounts
      return () => {
        clearInterval(interval);
        clearTimeout(timeout);
      };
    } else {
      FetchPastResults(setFormerResults);
    }
  }, [clickResult, analysisInProgress, newResultSaved]);

  const organizedResults = organizeResults(formerResults, t);

  return (
    <aside className="sidebar">
      <div className="login-area">
        <FontAwesomeIcon icon={faUserCircle} className="sidebar-avatar" />
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
                      className={`submenu-item ${activeLi === index ? 'selected' : ''}`}
                      onClick={() => { setActiveLi(index); handleResultClick(result);}}
                    >
                      <span>
                        {result.llm_result ? (
                          i18n.language === "fr" ? (
                            result.llm_result.french_title || result.taskId
                          ) : (
                            result.llm_result.english_title || result.taskId
                          )
                        ) : (
                          i18n.language === "fr" ? (
                            'Nouvelle requête' || result.taskId
                          ) : (
                            "New query" || result.taskId
                          )
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
        <FontAwesomeIcon icon={faSignOutAlt} />
        <p>{t("plateforme.sidebar.logout")}</p>
      </button>
    </aside>
  );
}

export default Sidebar;
