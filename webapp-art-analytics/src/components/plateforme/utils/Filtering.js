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
  filterRef,
  t
}) => (
    <div className="filter-buttons" ref={filterRef}>
        <button className="filter-icon" onClick={() => setFilterOpen(!filterOpen)}>
            <FontAwesomeIcon icon={faFilter} /> {t("plateforme.filtering.filtertitle")}
        </button>
        {filterOpen && (
            <div className="dropdown-content">
            <div className="filter-menu">
                <h4>{t("plateforme.filtering.pricetitle")}</h4>
                <label>
                {t("plateforme.filtering.minprice")}:
                <input
                    type="number"
                    value={minPrice}
                    onChange={(e) => handlePriceFilter(e.target.value, maxPrice)}
                />
                </label>
                <label>
                {t("plateforme.filtering.maxprice")}:
                <input
                    type="number"
                    value={maxPrice}
                    onChange={(e) => handlePriceFilter(minPrice, e.target.value)}
                />
                </label>
                <h4>{t("plateforme.filtering.datetitle")}</h4>
                <label>
                {t("plateforme.filtering.mindate")}:
                <input
                    type="date"
                    value={minDate}
                    onChange={(e) => handleDateFilter(e.target.value, maxDate)}
                />
                </label>
                <label>
                {t("plateforme.filtering.maxdate")}:
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