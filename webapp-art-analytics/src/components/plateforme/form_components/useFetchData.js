import { useEffect } from 'react';
import axios from 'axios';
import { URL_API, URL_GET_IDS_INFO, URL_API_BACK } from '../../../utils/constants';

const useFetchData = (result, setAdditionalData, setAvgMinEstimates, setAvgMaxEstimates, setAvgFinalResult, setNewResultSaved, setBotResult, setChatBotResultFetched, chatBotResultFetched) => {
  useEffect(() => {
    if (result && result.distances && result.ids) {
      const fetchData = async () => {
        try {
          const response = await axios.post(URL_API + URL_GET_IDS_INFO, {
            'ids': result.ids,
            'distances': result.distances,
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
  }, [result]);

  useEffect(() => {
    if (result && result.image && result.image.documents && !chatBotResultFetched) {
      const fetchLLM = async () => {
        try {
          const art_pieces = result.image.documents.flat();
          const response = await axios.post(URL_API_BACK + '/chatbot', { art_pieces: art_pieces });
          setBotResult(response.data.result)
          setChatBotResultFetched(true);
        } catch (error) {
          console.error('Error fetching additional data', error);
        }
      };
      fetchLLM();
    }
  }, [result, chatBotResultFetched]);
};

export default useFetchData;