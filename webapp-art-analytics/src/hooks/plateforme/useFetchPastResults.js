import { useEffect } from 'react';
import axiosInstance_middle from '../general/axiosInstance';
import { checkAuth } from '../general/identification';
import { useNavigate } from 'react-router-dom';
import Cookies from 'js-cookie';
import { URL_GET_TASK_RESULTS} from '../../utils/constants';

const useFetchPastResults = (newResultSaved, setFormerResults, setUserData) => {
  const navigate = useNavigate();
  useEffect(() => {
    const isAuthenticated = checkAuth();
    const userdataCookie = Cookies.get('userdata');

    if(isAuthenticated){
      if (userdataCookie) {
        try {
          const parsedUserdata = JSON.parse(userdataCookie);
          setUserData(parsedUserdata);

          axiosInstance_middle.get(`${URL_GET_TASK_RESULTS}?user_id=${parsedUserdata.id}`,
            {
              headers: {
                'Content-Type': 'application/json',
              },
            }
          )
            .then(response => {
              setFormerResults(response.data.results); 
            })
            .catch(error => {
              console.error('Error fetching former results:', error);
            });

        } catch (error) {
          console.error('Failed to parse userdata cookie:', error);
        }
      }
    } else {
      navigate('/login');
    }
    }, [newResultSaved, setFormerResults, setUserData]);
};

export default useFetchPastResults;