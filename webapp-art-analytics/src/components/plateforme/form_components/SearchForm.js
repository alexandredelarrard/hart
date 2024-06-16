import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch } from '@fortawesome/free-solid-svg-icons';

const SearchForm = ({ planExpired, closestVolumeExpired, text, file, handleSearchTextChange, handleSearchFileChange, handleSearchSubmit }) => (
  <div className="search-area">
    <form onSubmit={handleSearchSubmit} className="search-form">
      <FontAwesomeIcon icon={faSearch} className="search-icon" />
      <input 
        type="text" 
        value={text} 
        onChange={handleSearchTextChange} 
        placeholder="Enter description" 
        className="search-input" 
        disabled={planExpired || closestVolumeExpired}
      />
      <input 
        type="file" 
        onChange={handleSearchFileChange} 
        className="search-file-input"
        disabled={planExpired || closestVolumeExpired} 
      />
      <button type="submit" className="search-submit-button">Send for Analysis</button>
    </form>
    {planExpired && (
      <div className="plan-expired-message">
        Your trial period has ended. Please upgrade your plan.
      </div>
    )}
    {closestVolumeExpired && (
      <div className="query-expired-message">
        You reached the volume limit of possible queries allocated to your plan.
        Please update it to further query art pieces
      </div>
    )}
  </div>
);
export default SearchForm;