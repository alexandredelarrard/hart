import { useEffect } from 'react';
import Cookies from 'js-cookie';
import { useNavigate } from 'react-router-dom';
import axiosInstance_middle from '../general/axiosInstance';
import { checkAuth } from '../general/identification';
import { URL_GET_PAYMENTS } from '../../utils/constants';

const useFetchPayments = (setPayments) => {
  const navigate = useNavigate();
  useEffect(() => {
        const isAuthenticated = checkAuth();
        const userdataCookie = Cookies.get('userdata');

        if(isAuthenticated){
          if (userdataCookie) {
            const parsedUserdata = JSON.parse(userdataCookie);
            axiosInstance_middle.get(`${URL_GET_PAYMENTS}?user_id=${parsedUserdata.id}`, {}
            )
            .then(response => {
              setPayments(response.data.results);
            })
            .catch(error => {
                console.error('Error fetching former results:', error);
            });
        }
      } else {
        navigate("/login");
      }
      }, [setPayments]);
};

export default useFetchPayments;
