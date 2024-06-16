import Cookies from 'js-cookie';
import axios from 'axios';
import { URL_API, LOG_ACTIVITY} from './constants';

export const logActivity = async (activityType, activityDetails) => {
    try {
      const token = Cookies.get('token');
      if (!token) {
        return;
      }

      const userdataCookie = Cookies.get('userdata');
      if (userdataCookie) {
        const parsedUserdata = JSON.parse(userdataCookie);
    
        const response = await axios.post(URL_API + LOG_ACTIVITY, {
          user_id: parsedUserdata.id || '',
          activity_type: activityType,
          activity_details: activityDetails
        }, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
    
        return response.status === 201;
      } 
    } catch (error) {
      console.error('Error logging activity:', error);
      return false;
    }
  };