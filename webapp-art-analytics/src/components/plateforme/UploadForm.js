import React, { useState, useRef } from 'react';
import { CARDS_PER_PAGE } from '../../utils/constants';

import SearchForm from "./upload_utils/SearchForm.js";
import Pagination from './upload_utils/Pagination.js';
import Sorting from './upload_utils/Sorting.js';
import Filtering from './upload_utils/Filtering.js';
import ExpertCard from './upload_utils/ExpertCard.js';
import Card from './upload_utils/Card.js';

import CookieConsent from '../landing_page/CookieConsent.js';

import useFetchComplentaryResultData from '../../hooks/plateforme/useFetchComplentaryResultData.js';
import useFetchExperts from "../../hooks/plateforme/useFetchExperts.js";
import useNewSearchSubmit from '../../hooks/plateforme/useNewSearchSubmit.js';
import useLLMDesignation from '../../hooks/plateforme/useLLMDesignation.js';

import { formatPrice } from '../../utils/general.js';
import {
  handlePageChange,
  toggleShowAll,
  handleSortChange,
  handlePriceFilter,
  handleDateFilter,
  usePlanExpirationEffect,
  useClickOutsideEffect,
  getPaginatedData
} from './upload_utils/uploadFormUtils.js';

import '../../css/UploadForm.css';

function UploadForm({
  uploadFormState,
  uploadFormHandlers,
  setPlanExpired,
  planExpired,
  i18n,
  t
}) {
  const {
    searchfile,
    searchtext,
    file,
    text,
    taskId,
    result,
    botresult,
    chatBotResultFetched,
    additionalData,
    avgMinEstimates,
    avgMaxEstimates,
    avgFinalResult,
    experts,
    minPrice,
    maxPrice,
    minDate,
    maxDate,
  } = uploadFormState;

  const {
    setSearchFile,
    setSearchText,
    setFile,
    setText,
    setTaskId,
    setResult,
    setBotResult,
    setChatBotResultFetched,
    setAdditionalData,
    setAvgMaxEstimates,
    setAvgMinEstimates,
    setAvgFinalResult,
    setAnalysisInProgress,
    setNewResultSaved,
    setExperts,
    setMinPrice,
    setMaxPrice,
    setMinDate,
    setMaxDate,
    setActiveMenu
  } = uploadFormHandlers;

  const [currentPage, setCurrentPage] = useState(1);
  const [sortOrder, setSortOrder] = useState('relevance_desc');
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [filterOpen, setFilterOpen] = useState(false);
  const [showAll, setShowAll] = useState(false);
  const [closestVolumeExpired, setClosestVolumeExpired] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);

  const sortRef = useRef(null);
  const filterRef = useRef(null);

  const onDrop = acceptedFiles => {
    handleSearchFileChange(acceptedFiles[0]);
  };

  const handleRemoveImage = (event) => {
    event.stopPropagation();
    setSelectedImage(null);
    setFile(null);
  };

  const { fileUrl, handleSearchFileChange, handleSearchTextChange, handleSearchSubmit } = useNewSearchSubmit({
    file, text, setFile, setText,
    searchfile, searchtext, setSearchFile, setSearchText,
    setSelectedImage,
    setTaskId, setResult,
    setBotResult, setChatBotResultFetched,
    setAnalysisInProgress, setNewResultSaved,
    setAdditionalData, setAvgMinEstimates, setAvgMaxEstimates, setAvgFinalResult
  });

  const handlePageChangeHandler = handlePageChange(setCurrentPage);
  const toggleShowAllHandler = toggleShowAll(showAll, setShowAll);
  const handleSortChangeHandler = handleSortChange(setSortOrder, setDropdownOpen);
  const handlePriceFilterHandler = handlePriceFilter(setMinPrice, setMaxPrice);
  const handleDateFilterHandler = handleDateFilter(setMinDate, setMaxDate);

  usePlanExpirationEffect(setPlanExpired, setClosestVolumeExpired);
  useClickOutsideEffect(sortRef, filterRef, setDropdownOpen, setFilterOpen);

  const { paginatedData, totalPages } = getPaginatedData(additionalData, minPrice, maxPrice,
    minDate, maxDate, sortOrder, showAll, currentPage, CARDS_PER_PAGE);

  useFetchExperts(setExperts);
  useFetchComplentaryResultData(result, setAdditionalData, setAvgMinEstimates,
    setAvgMaxEstimates, setAvgFinalResult, setNewResultSaved);
  useLLMDesignation(taskId, additionalData, setNewResultSaved,
    chatBotResultFetched, setBotResult, setChatBotResultFetched);

  return (
    <div>
      <h2>{t("plateforme.uploadform.supertitle")}</h2>
      <SearchForm
        searchText={searchtext}
        onDrop={onDrop}
        selectedImage={selectedImage}
        setSelectedImage={setSelectedImage}
        planExpired={planExpired}
        handleRemoveImage= {handleRemoveImage}
        closestVolumeExpired={closestVolumeExpired}
        handleSearchTextChange={handleSearchTextChange}
        handleSearchSubmit={handleSearchSubmit}
        setActiveMenu={setActiveMenu}
        t={t}
      />
      {(fileUrl || text ) &&
      <div className="result-container">
        <div className="summary-area">
          <div className="part1">
            <div className="part-content">
              <div className="left">
                { fileUrl  ? (
                    <img src={fileUrl} alt="Uploaded" className="summary-image" />
                  ):(
                    <div className="card-detail-placeholder">
                      {t("overall.no_picture")}
                    </div>
                  ) }
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
                    <span className="card-price"><strong>{t("plateforme.uploadform.estimationprice")}:</strong> {formatPrice(avgMinEstimates, i18n.language, false)} - {formatPrice(avgMaxEstimates, i18n.language, true)}</span>
                    <span className="card-result"><strong>{t("plateforme.uploadform.finalprice")}:</strong> {formatPrice(avgFinalResult, i18n.language, true)}</span>
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
                handlePageChange={handlePageChangeHandler}
                showAll={showAll}
                toggleShowAll={toggleShowAllHandler}
                t={t}/>
               <div className='sorting-container'>
                  <Sorting
                    sortOrder={sortOrder}
                    handleSortChange={handleSortChangeHandler}
                    dropdownOpen={dropdownOpen}
                    setDropdownOpen={setDropdownOpen}
                    sortRef={sortRef}
                    t={t}/>
                  <Filtering
                    filterOpen={filterOpen}
                    setFilterOpen={setFilterOpen}
                    minPrice={minPrice}
                    maxPrice={maxPrice}
                    handlePriceFilter={handlePriceFilterHandler}
                    minDate={minDate}
                    maxDate={maxDate}
                    handleDateFilter={handleDateFilterHandler}
                    filterRef={filterRef}
                    t={t}/>
                </div>
            </div>
            <div className="card-container">
              {paginatedData.map((item, index) => (
                <Card
                  key={index}
                  item={item}
                  i18n={i18n}
                  t={t} />
              ))}
            </div>
            <div className="pagination-container">
              <Pagination
                totalPages={totalPages}
                currentPage={currentPage}
                handlePageChange={handlePageChangeHandler}
                showAll={showAll}
                toggleShowAll={toggleShowAllHandler}
                t={t}/>
            </div>
          </div>
        ) : (
          <></>
        )}
      </div>
      }
      <CookieConsent t={t}/>
    </div>
  );
}

export default UploadForm;
