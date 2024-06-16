import { useEffect } from 'react';
import axios from 'axios';
import { URL_API_BACK, URL_GET_TASK } from '../../../utils/constants';

const usePolling = (taskId, analysisInProgress, setResult, setAnalysisInProgress) => {
  useEffect(() => {
    if (taskId && analysisInProgress) {
      const interval = setInterval(async () => {
        try {
          const response = await axios.post(URL_API_BACK + URL_GET_TASK, {'taskid': taskId});

          if (response.data.state === 'SUCCESS') {
            setResult(response.data.result);
            clearInterval(interval);
            setAnalysisInProgress(false);
          }
        } catch (error) {
          console.error('Error fetching task result', error);
        }
      }, 1000); // Poll every X sec
      return () => clearInterval(interval);
    }
  }, [taskId, analysisInProgress]);
};

export default usePolling;