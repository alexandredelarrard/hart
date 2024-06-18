import { useEffect } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import { URL_API_BACK, URL_GET_TASK } from '../../utils/constants';

const useGetTaskResult = (taskId, analysisInProgress, setResult, setAnalysisInProgress) => {
  useEffect(() => {
    if (taskId && analysisInProgress) {
      const token = Cookies.get('token');
      if (!token) {
        return;
      }

      const interval = setInterval(async () => {
        try {
          const response = await axios.post(URL_API_BACK + URL_GET_TASK, {'taskid': taskId},{
            headers: {
               Authorization: `Bearer ${token}`,
               'Content-Type': 'application/json',
            },
          });

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
  }, [taskId, analysisInProgress, setResult, setAnalysisInProgress]);
};

export default useGetTaskResult;