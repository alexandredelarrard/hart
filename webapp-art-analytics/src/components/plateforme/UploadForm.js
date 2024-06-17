import React, { useState, useEffect} from 'react';
import Card from './Card';
import Cookies from 'js-cookie';
import '../../utils/utils_knn';
import {CARDS_PER_PAGE} from '../../utils/constants';

import '../../css/UploadForm.css';
import SearchForm from "./form_components/SearchForm.js";
import Pagination from './form_components/Pagination.js';
import HeaderPlateforme from "../landing_page/HeaderPlateforme.js";
import useFetchData from './form_components/useFetchData.js';
import usePolling from './form_components/usePolling.js';
import useUploadHandler from './form_components/useUploadHandler.js';
import CookieConsent from '../landing_page/CookieConsent.js'

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
    const userdata = Cookies.get('userdata');
    const remaining_closest_volume= Cookies.get('remaining_closest_volume');
    const remaining_search_volume= Cookies.get('remaining_search_volume');
    if (userdata) {
      const parsedUserdata = JSON.parse(userdata);
      const planEndDate = new Date(parsedUserdata.plan_end_date);
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
  }, []);

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

  const { fileUrl, handleSearchFileChange, handleSearchTextChange, handleSearchSubmit } = useUploadHandler({
    file, text, 
    setFile, setText, setTaskId, setResult, setBotResult, setChatBotResultFetched, setAnalysisInProgress,
    setAdditionalData, setAvgMinEstimates, setAvgMaxEstimates, setAvgFinalResult, setNewResultSaved
  });
  
  usePolling(taskId, analysisInProgress, setResult, setAnalysisInProgress);
  useFetchData(result, setAdditionalData, setAvgMinEstimates, setAvgMaxEstimates, setAvgFinalResult, setNewResultSaved, setBotResult, setChatBotResultFetched, chatBotResultFetched);
  
  return (
    <div className="upload-form-container">
      <HeaderPlateforme 
        handleMenuClick={handleMenuClick}
      />
        <SearchForm
            text={text}
            file={file}
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
                    {botresult &&<p><strong>Designation:</strong> {botresult}</p>}
                    <div className="card-footer">
                      <span className="card-price"><strong>Estimate:</strong> {avgMinEstimates}-{avgMaxEstimates} €</span>
                      <span className="card-result"><strong>Final:</strong> {avgFinalResult} €</span>
                    </div>
                  </div>
                </div>
            </div>
            <div className="part2">
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