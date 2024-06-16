import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch } from '@fortawesome/free-solid-svg-icons';

const SearchForm = ({ text, file, handleSearchTextChange, handleSearchFileChange, handleSearchSubmit }) => (
  <form onSubmit={handleSearchSubmit} className="search-form">
    <FontAwesomeIcon icon={faSearch} className="search-icon" />
    <input 
      type="text" 
      value={text} 
      onChange={handleSearchTextChange} 
      placeholder="Enter description" 
      className="search-input" 
    />
    <input 
      type="file" 
      onChange={handleSearchFileChange} 
      className="search-file-input" 
    />
    <button type="submit" className="search-submit-button">Send for Analysis</button>
  </form>
);
export default SearchForm;