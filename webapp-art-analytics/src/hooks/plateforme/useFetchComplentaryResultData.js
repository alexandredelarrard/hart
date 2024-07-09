import { useEffect, useRef } from 'react';
import axiosInstance_middle from '../general/axiosInstance';
import { URL_GET_IDS_INFO } from '../../utils/constants';
import { checkAuth } from '../general/identification';

const useFetchComplentaryResultData = (
  result,
  setAdditionalData,
  setAvgMinEstimates,
  setAvgMaxEstimates,
  setAvgFinalResult,
  setNewResultSaved) => {
  const setAdditionalDataRef = useRef(setAdditionalData);
  const setAvgMinEstimatesRef = useRef(setAvgMinEstimates);
  const setAvgMaxEstimatesRef = useRef(setAvgMaxEstimates);
  const setAvgFinalResultRef = useRef(setAvgFinalResult);
  const setNewResultSavedRef = useRef(setNewResultSaved);

  useEffect(() => {
    setAdditionalDataRef.current = setAdditionalData;
    setAvgMinEstimatesRef.current = setAvgMinEstimates;
    setAvgMaxEstimatesRef.current = setAvgMaxEstimates;
    setAvgFinalResultRef.current = setAvgFinalResult;
    setNewResultSavedRef.current = setNewResultSaved;
  }, [setAdditionalData, setAvgMinEstimates, setAvgMaxEstimates, setAvgFinalResult, setNewResultSaved]);

  useEffect(() => {
    if (result && result.answer) {
      const fetchData = async () => {
        try {
          const isAuthenticated = await checkAuth();

          if (isAuthenticated) {
            const response = await axiosInstance_middle.post(URL_GET_IDS_INFO, {
              'answer': result.answer
            }, {
              headers: {
                'Content-Type': 'application/json',
              },
            });

            // Ensure response.data is an array
            if (Array.isArray(response.data.result.answer)) {
              setAdditionalDataRef.current(response.data.result.answer); // Is a list
              setAvgMinEstimatesRef.current(response.data.min_estimate);
              setAvgMaxEstimatesRef.current(response.data.max_estimate);
              setAvgFinalResultRef.current(response.data.final_result);
            } else {
              console.error('Unexpected response format:', response.data);
            }
          } else {
            window.location.href = '/login';
            throw new Error('User not authenticated');
          }
        } catch (error) {
          console.error('Error fetching additional data', error);
        }
      };
      fetchData();
    }
  }, [result]);
};

export default useFetchComplentaryResultData;
