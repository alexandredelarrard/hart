import React, { useState, useEffect, useRef } from 'react';
import Cookies from 'js-cookie';
import { useTranslation } from 'react-i18next';
import { CARDS_PER_PAGE } from '../../utils/constants';

import SearchForm from "./upload_utils/SearchForm.js";
import Pagination from './upload_utils/Pagination.js';
import Sorting from './upload_utils/Sorting.js';
import Filtering from './upload_utils/Filtering.js';
import ExpertCard from './upload_utils/ExpertCard.js';
import Card from './upload_utils/Card.js';
import HeaderPlateforme from "./upload_utils/HeaderPlateforme.js";

import CookieConsent from '../landing_page/CookieConsent.js';

import useFetchComplentaryResultData from '../../hooks/plateforme/useFetchComplentaryResultData.js';
import useGetTaskResult from '../../hooks/plateforme/useGetTaskResult.js';
import useFetchExperts from "../../hooks/plateforme/useFetchExperts.js";
import useNewSearchSubmit from '../../hooks/plateforme/useNewSearchSubmit.js';
import useLLMDesignation from '../../hooks/plateforme/useLLMDesignation.js';

import '../../css/UploadForm.css';

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
  t
}) {
  
  const { i18n } = useTranslation('/analytics');
  const [currentPage, setCurrentPage] = useState(1);
  const [sortOrder, setSortOrder] = useState('relevance_desc');
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [filterOpen, setFilterOpen] = useState(false);
  const [showAll, setShowAll] = useState(false);
  const [planExpired, setPlanExpired] = useState(false);
  const [closestVolumeExpired, setclosestVolumeExpired] = useState(false);

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
    }
  }, [setPlanExpired, setclosestVolumeExpired]);

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
        // case 'relevance_asc':
        //   comparison = b.distances - a.distances;
        //   break;
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
        t={t}
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
                  <h2>{t("plateforme.uploadform.summarytitle")}</h2>
                </div>
                {text && <div> <strong>{t("plateforme.uploadform.specification")}</strong>: {text}</div>}
                {botresult &&
                  <>
                    <p><strong>{t("plateforme.uploadform.title")}:</strong> {botresult && i18n.language === "fr"? botresult.french_title : botresult.english_title}</p>
                    <p><strong>{t("plateforme.uploadform.designation")}:</strong> {botresult && i18n.language === "fr"? botresult.french_description : botresult.english_description}</p>
                  </>
                }
                {result &&
                  <div className="card-footer-summary">
                    <span className="card-price"><strong>{t("plateforme.uploadform.estimationprice")}:</strong> {avgMinEstimates}-{avgMaxEstimates} €</span>
                    <span className="card-result"><strong>{t("plateforme.uploadform.finalprice")}:</strong> {avgFinalResult} €</span>
                  </div>
                }
              </div>
            </div>
          </div>
          <div className="part2">
            <div className="part-content">
              <div className="middle">
                <div className="part-header common-title">
                  <h2>{t("plateforme.uploadform.experttitle")}</h2>
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
                toggleShowAll={toggleShowAll}
                t={t}/>
               <div className='sorting-container'>
                  <Sorting
                    sortOrder={sortOrder}
                    handleSortChange={handleSortChange}
                    dropdownOpen={dropdownOpen}
                    setDropdownOpen={setDropdownOpen}
                    sortRef={sortRef}
                    t={t}/>
                  <Filtering
                    filterOpen={filterOpen}
                    setFilterOpen={setFilterOpen}
                    minPrice={minPrice}
                    maxPrice={maxPrice}
                    handlePriceFilter={handlePriceFilter}
                    minDate={minDate}
                    maxDate={maxDate}
                    handleDateFilter={handleDateFilter}
                    filterRef={filterRef}
                    t={t}/>
                </div>
            </div>
            <div className="card-container">
              {paginatedData.map((item, index) => (
                <Card key={index} item={item} t={t} />
              ))}
            </div>
            <div className="pagination-container">
              <Pagination
                totalPages={totalPages}
                currentPage={currentPage}
                handlePageChange={handlePageChange}
                showAll={showAll}
                toggleShowAll={toggleShowAll}
                t={t}/>
            </div>
          </div>
        ) : (
          <></>
        )}
      </div>
      <CookieConsent t={t}/>
    </div>
  );
}

export default UploadForm;