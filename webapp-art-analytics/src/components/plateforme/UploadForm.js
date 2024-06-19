import React, { useState, useEffect, useRef } from 'react';
import Cookies from 'js-cookie';
import '../../utils/utils_knn';
import { CARDS_PER_PAGE } from '../../utils/constants';

import '../../css/UploadForm.css';
import SearchForm from "./utils/SearchForm.js";
import Pagination from './utils/Pagination.js';
import Sorting from './utils/Sorting.js';
import Filtering from './utils/Filtering.js';
import HeaderPlateforme from "../landing_page/HeaderPlateforme.js";
import CookieConsent from '../landing_page/CookieConsent.js';
import ExpertCard from './utils/ExpertCard.js';
import Card from './utils/Card';

import useFetchComplentaryResultData from '../../hooks/plateforme/useFetchComplentaryResultData.js';
import useGetTaskResult from '../../hooks/plateforme/useGetTaskResult.js';
import useFetchExperts from "../../hooks/plateforme/useFetchExperts.js";
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
  handleMenuClick,
  setMinPrice,
  setMaxPrice,
  setMinDate,
  setMaxDate,
  minPrice,
  maxPrice,
  minDate,
  maxDate,
}) {
  
  const [currentPage, setCurrentPage] = useState(1);
  const [sortOrder, setSortOrder] = useState('relevance_desc');
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [filterOpen, setFilterOpen] = useState(false);
  const [showAll, setShowAll] = useState(false);
  const [planExpired, setPlanExpired] = useState(false);
  const [closestVolumeExpired, setclosestVolumeExpired] = useState(false);
  const [searchVolumeExpired, setsearchVolumeExpired] = useState(false);

  const sortRef = useRef(null);
  const filterRef = useRef(null);

  const onDrop = acceptedFiles => {
    handleSearchFileChange(acceptedFiles[0]);
    setResult(null);
    setAdditionalData([]);
    setBotResult(null);
    setMinPrice('');
    setMaxPrice('');
    setMinDate('');
    setMaxDate('');
  };
  
  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };

  const toggleShowAll = () => {
    setShowAll(!showAll);
  };

  const handleSortChange = (newSortOrder) => {
    setSortOrder(newSortOrder);
    setDropdownOpen(false);
  };

  const handlePriceFilter = (min, max) => {
    setMinPrice(min);
    setMaxPrice(max);
  };

  const handleDateFilter = (min, max) => {
    setMinDate(min);
    setMaxDate(max);
  };

  useEffect(() => {
    const remaining_closest_volume = Cookies.get('remaining_closest_volume');
    const remaining_search_volume = Cookies.get('remaining_search_volume');
    const plan_end_date = Cookies.get('plan_end_date');
    if (plan_end_date) {
      const planEndDate = new Date(plan_end_date);
      const currentDate = new Date();
      if (currentDate > planEndDate) {
        setPlanExpired(true);
      }
      if (0 >= remaining_closest_volume) {
        setclosestVolumeExpired(true);
      }
      if (0 >= remaining_search_volume) {
        setsearchVolumeExpired(true);
      }
    }
  }, [setPlanExpired, setsearchVolumeExpired, setclosestVolumeExpired]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (sortRef.current && !sortRef.current.contains(event.target)) {
        setDropdownOpen(false);
      }
      if (filterRef.current && !filterRef.current.contains(event.target)) {
        setFilterOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [sortRef, filterRef]);

  const sortData = (data, sortOrder) => {
    const sortedData = data.sort((a, b) => {
      let comparison = 0;
      switch (sortOrder) {
        case 'relevance_desc':
          comparison = a.distances - b.distances;
          break;
        case 'relevance_asc':
          comparison = b.distances - a.distances;
          break;
        case 'price_desc':
          comparison = b.final_result - a.final_result;
          break;
        case 'price_asc':
          comparison = a.final_result - b.final_result;
          break;
        case 'date_desc':
          comparison = new Date(b.date) - new Date(a.date);
          break;
        case 'date_asc':
          comparison = new Date(a.date) - new Date(b.date);
          break;
        default:
          break;
      }
      return comparison;
    });

    return sortedData;
  };

  const filterData = (data, minPrice, maxPrice, minDate, maxDate) => {
    return data.filter(item => {
      const priceValid = (!minPrice || item.final_result >= minPrice) && (!maxPrice || item.final_result <= maxPrice);
      const dateValid = (!minDate || new Date(item.date) >= new Date(minDate)) && (!maxDate || new Date(item.date) <= new Date(maxDate));
      return priceValid && dateValid;
    });
  };

  const filteredData = filterData([...additionalData], minPrice, maxPrice, minDate, maxDate);
  const sortedData = sortData(filteredData, sortOrder);

  const paginatedData = showAll ? sortedData : sortedData.slice(
    (currentPage - 1) * CARDS_PER_PAGE,
    currentPage * CARDS_PER_PAGE
  );

  const totalPages = showAll ? 1 : Math.ceil(filteredData.length / CARDS_PER_PAGE);

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
        onDrop={onDrop}
        planExpired={planExpired}
        closestVolumeExpired={closestVolumeExpired}
        handleSearchTextChange={handleSearchTextChange}
        handleSearchSubmit={handleSearchSubmit}
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
                  <h2>Estimation proposée</h2>
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
                    <span className="card-price"><strong>Estimation:</strong> {avgMinEstimates}-{avgMaxEstimates} €</span>
                    <span className="card-result"><strong>Prix Final potentiel:</strong> {avgFinalResult} €</span>
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
                  {result && experts.map((expert, index) => (
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
            <div className="pagination-container">
              <Pagination
                totalPages={totalPages}
                currentPage={currentPage}
                handlePageChange={handlePageChange}
                showAll={showAll}
                toggleShowAll={toggleShowAll}/>
               <div className='sorting-container'>
                  <Sorting
                    sortOrder={sortOrder}
                    handleSortChange={handleSortChange}
                    dropdownOpen={dropdownOpen}
                    setDropdownOpen={setDropdownOpen}
                    sortRef={sortRef}/>
                  <Filtering
                    filterOpen={filterOpen}
                    setFilterOpen={setFilterOpen}
                    minPrice={minPrice}
                    maxPrice={maxPrice}
                    handlePriceFilter={handlePriceFilter}
                    minDate={minDate}
                    maxDate={maxDate}
                    handleDateFilter={handleDateFilter}
                    filterRef={filterRef}/>
                </div>
            </div>
            <div className="card-container">
              {paginatedData.map((item, index) => (
                <Card key={index} item={item} />
              ))}
            </div>
            <div className="pagination-container">
              <Pagination
                totalPages={totalPages}
                currentPage={currentPage}
                handlePageChange={handlePageChange}
                showAll={showAll}
                toggleShowAll={toggleShowAll}/>
            </div>
          </div>
        ) : (
          <></>
        )}
      </div>
      <CookieConsent />
    </div>
  );
}

export default UploadForm;