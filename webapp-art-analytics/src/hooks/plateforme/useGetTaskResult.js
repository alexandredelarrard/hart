import { useEffect } from 'react';
import axiosInstance_back from '../general/axiosInstanceBack';
import { useNavigate } from 'react-router-dom';
import { checkAuth } from '../general/identification';
import { URL_GET_TASK } from '../../utils/constants';

const useGetTaskResult = (taskId, analysisInProgress, setResult, setAnalysisInProgress) => {
  const navigate = useNavigate();
  useEffect(() => {
    if (taskId && analysisInProgress) {
      const isAuthenticated = checkAuth();

      if (isAuthenticated){
        const interval = setInterval(async () => {
          try {
            const response = await axiosInstance_back.post(URL_GET_TASK, {'taskid': taskId},{
              headers: {
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
    } else {
      navigate("/login");
    }
  }
  }, [taskId, analysisInProgress, setResult, setAnalysisInProgress]);
};

export default useGetTaskResult;
