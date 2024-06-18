import { useEffect } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import { checkAuth, logout } from '../general/identification';
import { URL_API, URL_GET_PAYMENTS } from '../../utils/constants';
import { useNavigate } from "react-router-dom";

const useFetchPayments = (setUserData, setName, setSurname, setAddress, setEmailValidated, setValidationDate, setPayments) => {
  
  const navigate = useNavigate();

  useEffect(() => {
        const token = Cookies.get('token');
        const checkUserAuth = async () => {
          const isAuthenticated = await checkAuth();
          if (!isAuthenticated) {
            await logout();
            navigate('/login'); // Redirect to the login page or home page if not authenticated
          }
        };
    
        checkUserAuth();
    
        const userdataCookie = Cookies.get('userdata');
        if (userdataCookie) {
          const parsedUserdata = JSON.parse(userdataCookie);
          setUserData(parsedUserdata);
          setName(parsedUserdata.name);
          setSurname(parsedUserdata.surname);
          setAddress(parsedUserdata.address || '');
          setEmailValidated(parsedUserdata.emailValidated || false);
          setValidationDate(parsedUserdata.creation_date || null);
    
          axios.get(`${URL_API + URL_GET_PAYMENTS}?user_id=${parsedUserdata.id}`,
            {
              headers: {
                Authorization: `Bearer ${token}`
              }
            }
          )
          .then(response => {
            setPayments(response.data.results); 
          })
          .catch(error => {
              console.error('Error fetching former results:', error);
          });
        }
      }, [navigate, setUserData, setName, setSurname, setAddress, setEmailValidated, setValidationDate, setPayments]);
};

export default useFetchPayments;
