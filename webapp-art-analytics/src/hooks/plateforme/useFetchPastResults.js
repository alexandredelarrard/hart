import { useEffect } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import { URL_API, URL_GET_TASK_RESULTS} from '../../utils/constants';

const useFetchPastResults = (newResultSaved, setFormerResults, setUserData) => {
  useEffect(() => {
    
    // required to ensure reloading sidebar sub items once new result is done
    
    const token = Cookies.get('token');
    const userdataCookie = Cookies.get('userdata');
    if (userdataCookie) {
      try {
        const parsedUserdata = JSON.parse(userdataCookie);
        setUserData(parsedUserdata);

        axios.get(`${URL_API + URL_GET_TASK_RESULTS}?user_id=${parsedUserdata.id}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
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
  }, [newResultSaved, setFormerResults, setUserData]);
};

export default useFetchPastResults;