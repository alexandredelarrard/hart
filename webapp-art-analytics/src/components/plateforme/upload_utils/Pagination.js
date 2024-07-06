import React from 'react';

import '../../../css/Pagination.css';

const Pagination = ({
  totalPages,
  currentPage,
  handlePageChange,
  showAll,
  toggleShowAll,
  t
}) => (

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
    <button
      className="show-all-button"
      onClick={toggleShowAll}
    >
      {showAll ? t("plateforme.pagination.showpages") : t("plateforme.pagination.showall")}
    </button>
  </div>
);

export default Pagination;
