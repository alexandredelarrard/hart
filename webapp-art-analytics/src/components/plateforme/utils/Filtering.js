import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFilter } from '@fortawesome/free-solid-svg-icons';

import '../../../css/Pagination.css';

const Filtering = ({
  filterOpen,
  setFilterOpen,
  minPrice,
  maxPrice,
  handlePriceFilter,
  minDate,
  maxDate,
  handleDateFilter,
  filterRef
}) => (
    <div className="filter-buttons" ref={filterRef}>
        <button className="filter-icon" onClick={() => setFilterOpen(!filterOpen)}>
            <FontAwesomeIcon icon={faFilter} /> Filtrer
        </button>
        {filterOpen && (
            <div className="dropdown-content">
            <div className="filter-menu">
                <h4>Prix</h4>
                <label>
                Prix Min:
                <input
                    type="number"
                    value={minPrice}
                    onChange={(e) => handlePriceFilter(e.target.value, maxPrice)}
                />
                </label>
                <label>
                Prix Max:
                <input
                    type="number"
                    value={maxPrice}
                    onChange={(e) => handlePriceFilter(minPrice, e.target.value)}
                />
                </label>
                <h4>Date</h4>
                <label>
                Date Min:
                <input
                    type="date"
                    value={minDate}
                    onChange={(e) => handleDateFilter(e.target.value, maxDate)}
                />
                </label>
                <label>
                Date Max:
                <input
                    type="date"
                    value={maxDate}
                    onChange={(e) => handleDateFilter(minDate, e.target.value)}
                />
                </label>
            </div>
            </div>
        )}
    </div>
);

export default Filtering;