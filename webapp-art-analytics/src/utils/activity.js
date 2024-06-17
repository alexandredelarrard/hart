import Cookies from 'js-cookie';
import axios from 'axios';
import { URL_API, LOG_ACTIVITY } from './constants';

export const logActivity = async (activityType, activityDetails) => {
  try {
    const token = Cookies.get('token');
    if (!token) {
      return;
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
    }
  } catch (error) {
    console.error('Error logging activity:', error);
    return false;
  }
};