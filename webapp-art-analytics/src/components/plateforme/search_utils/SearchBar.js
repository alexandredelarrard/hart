import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch } from '@fortawesome/free-solid-svg-icons';
import { Link } from 'react-router-dom';
import searchDb from '../../../hooks/search/searchDb.js'
import "../../../css/SearchForm.css";

const SearchBar = ({ 
  searchText,
  setSearchText,
  setSearchResults, 
  planExpired, 
  searchVolumeExpired, 
  handleMenuClick,
  t 
}) => {
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const isError = planExpired || searchVolumeExpired;

  const handleSearchTextChange = (text) => {
    setSearchText(text);
  };

  const handleInputChange = (e) => {
    handleSearchTextChange(e.target.value);
  };

  const handleSearch = (e) => {
    searchDb({ e, setError, setLoading, setSearchResults, searchText, isError });
  };

  return (
    <div className="search-area">
      <form onSubmit={handleSearch} className="search-form">
        <div className="form-row">
          <input 
            type="text" 
            value={searchText} 
            onChange={handleInputChange} 
            placeholder={t("plateforme.search.textareadesc")}
            className={`search-input ${isError ? 'input-error' : ''}`} 
            disabled={isError}
          />
          <button type="submit" className="search-submit-button" disabled={isError || loading}>
            <FontAwesomeIcon icon={faSearch} />
          </button>
        </div>
      </form>
      <div className={`error-message-search ${isError ? 'show' : ''}`}>
        {planExpired && (
          <div className="plan-expired-message">
            {t("plateforme.search.errorplanexpired")} <Link to="/subscribe">{t("plateforme.search.upgradebutton")}</Link>.
          </div>
        )}
        {searchVolumeExpired && (
          <div className="query-expired-message">
            {t("plateforme.search.errorsearchvolume")} <button className='button-error-plan' onClick={() => { handleMenuClick("my-offers")}}>{t("plateforme.search.upgradebutton")}</button>
          </div>
        )}
      </div>
      {loading && <p>Loading...</p>}
      {error && <p className="error-message">{error}</p>}
    </div>
  );
};

export default SearchBar;