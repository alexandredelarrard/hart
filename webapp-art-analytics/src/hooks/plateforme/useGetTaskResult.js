import { useEffect } from 'react';
import axiosInstance_back from '../general/axiosInstanceBack';
import { checkAuth } from '../general/identification';
import { URL_GET_TASK } from '../../utils/constants';

const useGetTaskResult = (taskId, result, setResult, setActiveLi) => {
  useEffect(() => {
    if (taskId && !result) {
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
              setActiveLi(0);
              clearInterval(interval);
            }
          } catch (error) {
            console.error('Error fetching task result', error);
          }
        }, 1500); // Poll every X sec
        return () => clearInterval(interval);
    } else {
      window.location.href = "/login"
    }
  }
  }, [taskId, setResult]);
};

export default useGetTaskResult;
