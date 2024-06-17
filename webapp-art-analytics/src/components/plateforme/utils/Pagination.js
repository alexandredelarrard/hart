import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSort, faCalendarAlt, faDollarSign, faMapMarkerAlt } from '@fortawesome/free-solid-svg-icons';

const Pagination = ({ totalPages, currentPage, handlePageChange, sortOrder, handleSortChange, dropdownOpen, setDropdownOpen }) => (
  <div className="pagination">
    {Array.from({ length: totalPages }, (_, index) => (
      <button
        key={index + 1}
        className={`pagination-button ${currentPage === index + 1 ? 'active' : ''}`}
        onClick={() => handlePageChange(index + 1)}
      >
        {index + 1}
      </button>
    ))}
    <div className="sort-buttons">
      <div className="dropdown">
        <button onClick={() => setDropdownOpen(!dropdownOpen)} className="dropbtn">
          <FontAwesomeIcon icon={faSort} /> Sort
        </button>
        {dropdownOpen && (
          <div className="dropdown-content">
            <button onClick={() => handleSortChange('distance')} className={`sort-button ${sortOrder === 'distance' ? 'active' : ''}`}>
              <FontAwesomeIcon icon={faMapMarkerAlt} /> Relevance
            </button>
            <button onClick={() => handleSortChange('date')} className={`sort-button ${sortOrder === 'date' ? 'active' : ''}`}>
              <FontAwesomeIcon icon={faCalendarAlt} /> Date
            </button>
            <button onClick={() => handleSortChange('final_price')} className={`sort-button ${sortOrder === 'final_price' ? 'active' : ''}`}>
              <FontAwesomeIcon icon={faDollarSign} /> Final Price
            </button>
          </div>
        )}
      </div>
    </div>
  </div>
);

export default Pagination;