import { useEffect } from 'react';
import Cookies from 'js-cookie';
import { sortData } from '../../../utils/sorting_function';

export const handlePageChange = (setCurrentPage) => (newPage) => {
  setCurrentPage(newPage);
};

export const toggleShowAll = (showAll, setShowAll) => () => {
  setShowAll(!showAll);
};

export const handleSortChange = (setSortOrder, setDropdownOpen) => (newSortOrder) => {
  setSortOrder(newSortOrder);
  setDropdownOpen(false);
};

export const handlePriceFilter = (setMinPrice, setMaxPrice) => (min, max) => {
  setMinPrice(min);
  setMaxPrice(max);
};

export const handleDateFilter = (setMinDate, setMaxDate) => (min, max) => {
  setMinDate(min);
  setMaxDate(max);
};

export const usePlanExpirationEffect = (setPlanExpired, setClosestVolumeExpired) => {
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
        setClosestVolumeExpired(true);
      }
    }
  }, [setPlanExpired, setClosestVolumeExpired]);
};

export const useClickOutsideEffect = (sortRef, filterRef, setDropdownOpen, setFilterOpen) => {
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
  }, [sortRef, filterRef, setDropdownOpen, setFilterOpen]);
};


const filterData = (data, minPrice, maxPrice, minDate, maxDate) => {
  return data.filter(item => {
    const priceValid = (!minPrice || item.final_result >= minPrice) && (!maxPrice || item.final_result <= maxPrice);
    const dateValid = (!minDate || new Date(item.date) >= new Date(minDate)) && (!maxDate || new Date(item.date) <= new Date(maxDate));
    return priceValid && dateValid;
  });
};

export const getPaginatedData = (additionalData, minPrice, maxPrice, minDate, maxDate, sortOrder, showAll, currentPage, CARDS_PER_PAGE) => {
  const filteredData = filterData([...additionalData], minPrice, maxPrice, minDate, maxDate);
  const sortedData = sortData(filteredData, sortOrder);

  const paginatedData = showAll ? sortedData : sortedData.slice(
    (currentPage - 1) * CARDS_PER_PAGE,
    currentPage * CARDS_PER_PAGE
  );

  const totalPages = showAll ? 1 : Math.ceil(filteredData.length / CARDS_PER_PAGE);

  return { paginatedData, totalPages };
};
