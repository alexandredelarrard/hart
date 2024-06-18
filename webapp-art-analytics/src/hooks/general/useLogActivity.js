import { useCallback } from 'react';
import Cookies from 'js-cookie';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { checkAuth } from './identification';
import { URL_API, LOG_ACTIVITY } from '../../utils/constants';

const useLogActivity = () => {
  const navigate = useNavigate();

  const logActivity = useCallback(async (activityType, activityDetails) => {
    try {
      const token = Cookies.get('token');
      const isAuthenticated = await checkAuth();

      if (!isAuthenticated) {
        navigate('/login'); // Redirect to the login page or home page if not authenticated
        return false;
      }

      const userdataCookie = Cookies.get('userdata');

      if (userdataCookie) {
        const parsedUserdata = JSON.parse(userdataCookie);
        const userId = parsedUserdata.id || '';
        const machineSpecs = Cookies.get('machineSpecs');
        const geolocation = Cookies.get('geolocation');

        const response = await axios.post(
          URL_API + LOG_ACTIVITY,
          {
            user_id: userId,
            activity_type: activityType,
            activity_details: activityDetails,
            machineSpecs: machineSpecs ? JSON.parse(machineSpecs) : null,
            geolocation: geolocation ? JSON.parse(geolocation) : null,
          },
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        return response.status === 201;
      } else {
        console.warn('User data cookie is not available.');
        return false;
      }
    } catch (error) {
      console.error('Error logging activity:', error);
      return false;
    }
  }, [navigate]);

  return logActivity;
};

export default useLogActivity;