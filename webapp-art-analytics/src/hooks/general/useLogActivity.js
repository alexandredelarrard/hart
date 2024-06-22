import { useCallback } from 'react';
import Cookies from 'js-cookie';
import axiosInstance_middle from '../general/axiosInstance';
import { useNavigate } from 'react-router-dom';
import { checkAuth} from './identification';
import { LOG_ACTIVITY } from '../../utils/constants';

const useLogActivity = () => {
  const navigate = useNavigate();
  const logActivity = useCallback(async (activityType, activityDetails) => {
    try {
      const isAuthenticated = await checkAuth();
      const userdataCookie = Cookies.get('userdata');

      if (isAuthenticated){
        if (userdataCookie ) {
          const parsedUserdata = JSON.parse(userdataCookie);
          const userId = parsedUserdata.id || '';
          const machineSpecs = Cookies.get('machineSpecs');
          const geolocation = Cookies.get('geolocation');

          const response = await axiosInstance_middle.post(
            LOG_ACTIVITY,
            {
              user_id: userId,
              activity_type: activityType,
              activity_details: activityDetails,
              machineSpecs: machineSpecs ? JSON.parse(machineSpecs) : null,
              geolocation: geolocation ? JSON.parse(geolocation) : null,
            }, {}
          );

          return response.status === 201;
        } else {
          console.warn('User data cookie is not available.');
          return false;
        }
    } else {
      navigate('/login');
    }
    } catch (error) {
      console.error('Error logging activity:', error);
      return false;
    }
  }, []);

  return logActivity;
};

export default useLogActivity;