import { useEffect } from 'react';
import axiosInstance_middle from '../general/axiosInstance';
import { URL_GET_IDS_INFO } from '../../utils/constants';
import { checkAuth } from '../general/identification';

const useFetchComplentaryResultData = (result, setAdditionalData, setAvgMinEstimates, setAvgMaxEstimates, setAvgFinalResult, setNewResultSaved) => {
  useEffect(() => {
    if (result && result.answer) {
      const fetchData = async () => {
        try {
            const isAuthenticated = await checkAuth();

            if(isAuthenticated){
              const response = await axiosInstance_middle.post(URL_GET_IDS_INFO, {
                'answer': result.answer
              },{
                headers: {
                  'Content-Type': 'application/json',
                },
              });

              // Ensure response.data is an array
              if (Array.isArray(response.data.result.answer)) {
                setAdditionalData(response.data.result.answer);
                setAvgMinEstimates(response.data.min_estimate);
                setAvgMaxEstimates(response.data.max_estimate);
                setAvgFinalResult(response.data.final_result);
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
  }, [result, setAdditionalData, setAvgMinEstimates, setAvgMaxEstimates, setAvgFinalResult, setNewResultSaved]);

};

export default useFetchComplentaryResultData;
