import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faImage, faEdit, faUserCircle, faSignOutAlt, faChevronRight, faChevronDown, faTrash } from '@fortawesome/free-solid-svg-icons';
import { useTranslation } from 'react-i18next';
import Cookies from 'js-cookie';

import { organizeResults } from './upload_utils/organizeSidebar.js';
import { URL_API, URL_DELETE_TASK_RESULT, PATHS } from '../../utils/constants';

import { logout, checkAuth } from '../../hooks/general/identification';
import useLogActivity from '../../hooks/general/useLogActivity.js';
import FetchPastResults from '../../hooks/plateforme/FetchPastResults.js';
import useGetTaskResult from '../../hooks/plateforme/useGetTaskResult.js';


import '../../css/Sidebar.css';

function Sidebar({
  userData,
  setUserData,
  uploadFormHandlers,
  uploadFormState,
  t
}) {
  const {
    taskId,
    result,
    activeMenu,
    activeLi,
    showResults,
    chatBotResultFetched
  } = uploadFormState;

  const {
    setActiveMenu,
    setActiveLi,
    setShowResults,
    setResult
  } = uploadFormHandlers;

  const [formerResults, setFormerResults] = useState([]);
  const [clickResult, setClickResult] = useState(false);
  const { i18n } = useTranslation(PATHS["ANALYTICS"]);
  const LogActivity = useLogActivity();

  const memoizedSetResult = useCallback((newResult) => {
    setResult(newResult);
  }, [uploadFormState]);

  const memoizedSetActiveLi = useCallback((index) => {
    setActiveLi(index);
  }, [setActiveLi]);

  // Logout on click button
  const handleLogout = async () => {
    await LogActivity("click_log_out", "");

    memoizedSetResult(null);
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

    if (result.file) {
      const byteCharacters = atob(result.file);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'image/jpg' });
      uploadFormHandlers.setFile(blob);
    } else {
      uploadFormHandlers.setFile(null);
    }
    uploadFormHandlers.setText(result.text);
    memoizedSetResult({ answer: result.answer });
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
      } else {
        window.location.href = PATHS["LOGIN"];
      }

  }, [setUserData]);

  useGetTaskResult(taskId, result, memoizedSetResult, memoizedSetActiveLi);

  useEffect(() => {
    if (activeMenu === 'closest-lots') {
      FetchPastResults(setFormerResults);
    }
  }, [clickResult, activeMenu, chatBotResultFetched]);

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
          onClick={() => { setActiveMenu('search-art'); toggleResults(false); }}
        >
          <FontAwesomeIcon icon={faImage} className="menu-icon" />
          {t("plateforme.sidebar.search")}
        </li>
        <li
          className={`menu-item ${activeMenu === 'closest-lots' ? 'active' : ''}`}
          onClick={() => { setActiveMenu('closest-lots'); toggleResults(true); }}
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
                      key={category + index}
                      className={`submenu-item ${activeLi === category + index ? 'selected' : ''}`}
                      onClick={() => { memoizedSetActiveLi(category + index); handleResultClick(result);}}
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
                            'Nouvelle recherche' || result.taskId
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
          onClick={() => { setActiveMenu('optimize-sale'); toggleResults(false); }}
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
