import { useEffect, useCallback } from 'react';
import axiosInstance_middle from '../general/axiosInstance';
import { checkAuth } from '../general/identification';
import { URL_MY_ACTIVITY } from '../../utils/constants';
import {generateDatesRange} from '../../utils/general.js';

const useFetchMyActivity = (setActivityData) => {

  const fetchActivityData = useCallback(async () => {
        try {
          const response = await axiosInstance_middle.get(URL_MY_ACTIVITY);
          const rawData = response.data.result;

          // Get the first date in the data and today's date
          const startDate = new Date(rawData[0]?.date || new Date());
          const endDate = new Date();

          const allDates = generateDatesRange(startDate, endDate);

          const dataMap = rawData.reduce((acc, item) => {
            acc[item.date] = item;
            return acc;
          }, {});

          // Merge generated dates with raw data
          const filledData = allDates.map(date => {
            const dateString = date.toISOString().split('T')[0]; // Convert to YYYY-MM-DD format
            return {
              date: dateString,
              estimateVolume: dataMap[dateString]?.estimateVolume || 0,
              searchVolume: dataMap[dateString]?.searchVolume || 0
            };
          });

          setActivityData(filledData);
        } catch (error) {
          console.error("Error fetching activity data", error);
        }
    }, [setActivityData]);

    useEffect(() => {
      const isAuthenticated = checkAuth();
      if(isAuthenticated){
        fetchActivityData();
      }
      }, [fetchActivityData]);

};

export default useFetchMyActivity;
