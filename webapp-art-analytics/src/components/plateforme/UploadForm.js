import React, { useState, useEffect} from 'react';
import Cookies from 'js-cookie';
import '../../utils/utils_knn';
import {CARDS_PER_PAGE} from '../../utils/constants';

import '../../css/UploadForm.css';
import SearchForm from "./utils/SearchForm.js";
import Pagination from './utils/Pagination.js';
import HeaderPlateforme from "../landing_page/HeaderPlateforme.js";
import CookieConsent from '../landing_page/CookieConsent.js';
import ExpertCard from './utils/ExpertCard.js';
import Card from './utils/Card';

import useFetchComplentaryResultData from '../../hooks/plateforme/useFetchComplentaryResultData.js';
import useGetTaskResult from '../../hooks/plateforme/useGetTaskResult.js';
import useFetchExperts from "../../hooks/plateforme/useFetchExperts.js"
import useNewSearchSubmit from '../../hooks/plateforme/useNewSearchSubmit.js';
import useLLMDesignation from '../../hooks/plateforme/useLLMDesignation.js';

function UploadForm({
  setFile,
  setText,
  setTaskId,
  taskId,
  file,
  text,
  result,
  setResult,
  botresult,
  setBotResult,
  chatBotResultFetched,
  setChatBotResultFetched,
  additionalData,
  setAdditionalData,
  avgMinEstimates,
  avgMaxEstimates,
  setAvgMaxEstimates,
  setAvgMinEstimates,
  avgFinalResult,
  setAvgFinalResult,
  analysisInProgress,
  setAnalysisInProgress,
  setNewResultSaved,
  setExperts,
  experts,
  handleMenuClick
}) {
  
  const [currentPage, setCurrentPage] = useState(1);
  const [sortOrder, setSortOrder] = useState('distance');
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [planExpired, setPlanExpired] = useState(false);
  const [closestVolumeExpired, setclosestVolumeExpired] = useState(false);
  const [searchVolumeExpired, setsearchVolumeExpired] = useState(false);
  
  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };

  const handleSortChange = (newSortOrder) => {
    setSortOrder(newSortOrder);
    setDropdownOpen(false)
  };

  useEffect(() => {
    const remaining_closest_volume= Cookies.get('remaining_closest_volume');
    const remaining_search_volume= Cookies.get('remaining_search_volume');
    const plan_end_date= Cookies.get('plan_end_date');
    if (plan_end_date) {
      const planEndDate = new Date(plan_end_date);
      const currentDate = new Date();
      if (currentDate > planEndDate) {
        setPlanExpired(true);
      }
      if(0>=remaining_closest_volume ){
        setclosestVolumeExpired(true)
      }
      if(0>=remaining_search_volume ){
        setsearchVolumeExpired(true)
      }
    }
  }, [setPlanExpired, setsearchVolumeExpired, setclosestVolumeExpired]);

  const sortData = (data, sortOrder) => {
    switch (sortOrder) {
      case 'date':
        return data.sort((a, b) => new Date(b.date) - new Date(a.date));
      case 'final_price':
        return data.sort((a, b) => b.final_result - a.final_result);
      case 'distance':
      default:
        return data.sort((a, b) => a.distances - b.distances);
    }
  };

  const sortedData = sortData([...additionalData], sortOrder);

  const paginatedData = sortedData.slice(
    (currentPage - 1) * CARDS_PER_PAGE,
    currentPage * CARDS_PER_PAGE
  );

  const totalPages = Math.ceil(additionalData.length / CARDS_PER_PAGE);

  const { fileUrl, handleSearchFileChange, handleSearchTextChange, handleSearchSubmit } = useNewSearchSubmit({
    file, text, 
    setFile, setText, setTaskId, setResult, setBotResult, setChatBotResultFetched, setAnalysisInProgress,
    setAdditionalData, setAvgMinEstimates, setAvgMaxEstimates, setAvgFinalResult, setNewResultSaved
  });
  useFetchExperts(setExperts);
  useGetTaskResult(taskId, analysisInProgress, setResult, setAnalysisInProgress);
  useFetchComplentaryResultData(result, setAdditionalData, setAvgMinEstimates, setAvgMaxEstimates, setAvgFinalResult, setNewResultSaved);
  useLLMDesignation(taskId, additionalData, setNewResultSaved, chatBotResultFetched, setBotResult, setChatBotResultFetched);

  return (
    <div className="upload-form-container">
      <HeaderPlateforme 
        handleMenuClick={handleMenuClick}
      />
        <SearchForm
            text={text}
            file={file}
            setResult={setResult}
            setAdditionalData={setAdditionalData}
            handleSearchTextChange={handleSearchTextChange}
            handleSearchFileChange={handleSearchFileChange}
            handleSearchSubmit={handleSearchSubmit}
            planExpired={planExpired}
            closestVolumeExpired={closestVolumeExpired}
            handleMenuClick={handleMenuClick}
          />
        <div className="result-container">
          <div className="summary-area">
            <div className="part1">
                <div className="part-content">
                  <div className="left">
                    {fileUrl && <img src={fileUrl} alt="Uploaded" className="summary-image" />}
                  </div>
                  <div className="middle">
                    <div className="part-header common-title">
                      <h2>Estimation</h2>
                  </div>
                  {text && <div> <strong>Specification:</strong>: {text}</div>}
                    {botresult &&
                    <>
                      <p><strong>Titre:</strong> {botresult.french_title}</p>
                      <p><strong>Designation:</strong> {botresult.french_description}</p>
                    </>
                    }
                    {result &&
                    <div className="card-footer-summary">
                      <span className="card-price"><strong>Estimate:</strong> {avgMinEstimates}-{avgMaxEstimates} €</span>
                      <span className="card-result"><strong>Final:</strong> {avgFinalResult} €</span>
                    </div>
                  }
                  </div>
                </div>
            </div>
            <div className="part2">
              <div className="part-content">
              <div className="middle">
                <div className="part-header common-title">
                  <h2>Les Experts à proximité</h2>
                </div>
                  <div className="experts-list">
                    {result&&experts.map((expert, index) => (
                      <ExpertCard key={index} expert={expert} />
                    ))}
                </div>
              </div>
              </div>
            </div>
          </div>
          <div className="delimiter-line"></div>
          {additionalData.length > 0 ? (
            <div className="additional-data">
              <Pagination
                totalPages={totalPages}
                currentPage={currentPage}
                handlePageChange={handlePageChange}
                sortOrder={sortOrder}
                handleSortChange={handleSortChange}
                dropdownOpen={dropdownOpen}
                setDropdownOpen={setDropdownOpen}
              />
              <div className="card-container">
                {paginatedData.map((item, index) => (
                  <Card key={index} item={item} />
                ))}
              </div>
            </div>
            ) : (
            <p></p>
          )}
        </div>
        <CookieConsent />
    </div>
  );
}

export default UploadForm;