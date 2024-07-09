import axiosInstance_middle from '../general/axiosInstance';
import { checkAuth } from '../general/identification';
import Cookies from 'js-cookie';
import { URL_GET_TASK_RESULTS } from '../../utils/constants';

const FetchPastResults = async (setFormerResults) => {

      const isAuthenticated = await checkAuth();
      const userdataCookie = Cookies.get('userdata');

      if (isAuthenticated) {
        if (userdataCookie) {
          try {
            const parsedUserdata = JSON.parse(userdataCookie);
            const response = await axiosInstance_middle.get(`${URL_GET_TASK_RESULTS}?user_id=${parsedUserdata.id}`, {
              headers: {
                'Content-Type': 'application/json',
              },
            });

            setFormerResults(response.data.results);

          } catch (error) {
            console.error('Error fetching former results:', error);
          }
        }
      } else {
        window.location.href = '/login';
      }
};

export default FetchPastResults;
