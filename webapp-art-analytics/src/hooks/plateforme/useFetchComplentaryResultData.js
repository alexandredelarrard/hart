import { useEffect } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import { URL_API, URL_GET_IDS_INFO } from '../../utils/constants';

const useFetchComplentaryResultData = (result, setAdditionalData, setAvgMinEstimates, setAvgMaxEstimates, setAvgFinalResult, setNewResultSaved) => {
  useEffect(() => {
    if (result && result.distances && result.ids) {
      const fetchData = async () => {
        try {
          const token = Cookies.get('token');
          if (!token) {
            return;
          }

          const response = await axios.post(URL_API + URL_GET_IDS_INFO, {
            'ids': result.ids,
            'distances': result.distances,
          },{
            headers: {
               Authorization: `Bearer ${token}`,
               'Content-Type': 'application/json',
            },
          });

          // Ensure response.data is an array
          if (Array.isArray(response.data.result)) {
            setAdditionalData(response.data.result);
            setAvgMinEstimates(response.data.min_estimate);
            setAvgMaxEstimates(response.data.max_estimate);
            setAvgFinalResult(response.data.final_result);
          } else {
            console.error('Unexpected response format:', response.data);
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
