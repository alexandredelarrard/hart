import { useEffect } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import { URL_API, URL_GET_IDS_INFO, URL_API_BACK } from '../../utils/constants';

const useFetchData = (result, setAdditionalData, setAvgMinEstimates, setAvgMaxEstimates, setAvgFinalResult, setNewResultSaved, setBotResult, setChatBotResultFetched, chatBotResultFetched) => {
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
            setNewResultSaved(true);
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

  useEffect(() => {
    if (result && result.image && result.image.documents && !chatBotResultFetched) {
      const fetchLLM = async () => {
        try {
          const token = Cookies.get('token');
          if (!token) {
            return;
          }
          
          const art_pieces = result.image.documents.flat();
          const response = await axios.post(URL_API_BACK + '/chatbot', { art_pieces: art_pieces },{
            headers: {
               Authorization: `Bearer ${token}`,
               'Content-Type': 'application/json',
            },
          });
          setBotResult(response.data.result)
          setChatBotResultFetched(true);
        } catch (error) {
          console.error('Error fetching additional data', error);
        }
      };
      fetchLLM();
    }
  }, [result, chatBotResultFetched, setBotResult, setChatBotResultFetched]);
};

export default useFetchData;