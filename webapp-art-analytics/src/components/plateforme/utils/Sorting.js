import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSort, faCalendarAlt, faDollarSign, faMapMarkerAlt } from '@fortawesome/free-solid-svg-icons';

import '../../../css/Pagination.css';

const Sorting = ({
  sortOrder,
  handleSortChange,
  dropdownOpen,
  setDropdownOpen,
  sortRef
}) => (
    <div className="sort-filter-container">
      <div className="sort-buttons" ref={sortRef}>
        <button onClick={() => setDropdownOpen(!dropdownOpen)} className="dropbtn">
          <FontAwesomeIcon icon={faSort} /> Trier
        </button>
        {dropdownOpen && (
          <div className="dropdown-content">
            <button
              onClick={() => handleSortChange('relevance_desc')}
              className={`sort-button ${sortOrder === 'relevance_desc' ? 'active' : ''}`}
            >
              <FontAwesomeIcon icon={faMapMarkerAlt} /> Relevance (High to Low)
            </button>
            <button
              onClick={() => handleSortChange('relevance_asc')}
              className={`sort-button ${sortOrder === 'relevance_asc' ? 'active' : ''}`}
            >
              <FontAwesomeIcon icon={faMapMarkerAlt} /> Relevance (Low to High)
            </button>
            <button
              onClick={() => handleSortChange('price_desc')}
              className={`sort-button ${sortOrder === 'price_desc' ? 'active' : ''}`}
            >
              <FontAwesomeIcon icon={faDollarSign} />  Price (High to Low)
            </button>
            <button
              onClick={() => handleSortChange('price_asc')}
              className={`sort-button ${sortOrder === 'price_asc' ? 'active' : ''}`}
            >
              <FontAwesomeIcon icon={faDollarSign} /> Price (Low to High)
            </button>
            <button
              onClick={() => handleSortChange('date_desc')}
              className={`sort-button ${sortOrder === 'date_desc' ? 'active' : ''}`}
            >
              <FontAwesomeIcon icon={faCalendarAlt} /> Date (High to Low)
            </button>
            <button
              onClick={() => handleSortChange('date_asc')}
              className={`sort-button ${sortOrder === 'date_asc' ? 'active' : ''}`}
            >
              <FontAwesomeIcon icon={faCalendarAlt} /> Date (Low to High)
            </button>
          </div>
        )}
      </div>
    </div>
);

export default Sorting;