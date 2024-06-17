import axios from 'axios';
import Cookies from 'js-cookie';
import { URL_API, URL_CHECK_LOGIN, URL_LOGOUT, URL_REFRESH_LOGIN } from './constants';


export const logout = async () => {
  try {
    const response = await axios.post(URL_API + URL_LOGOUT, {}, {
      headers: {
        Authorization: `Bearer ${Cookies.get('token')}`
      }
    });
    if (response.status === 200) {
      Cookies.remove('token');
      Cookies.remove('refresh_token');
      Cookies.remove('userdata');
      Cookies.remove('plan_end_date');
      Cookies.remove('remaining_closest_volume');
      Cookies.remove('remaining_search_volume');
    }
  } catch (error) {
    console.error('Error logging out:', error);
  }
};

export const checkAuth = async () => {
  try {
    const token = Cookies.get('token');
    if (!token) {
      return false;
    }

    const response = await axios.get(URL_API + URL_CHECK_LOGIN, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.status === 200;
  } catch (error) {
    if (error.response && error.response.status === 401) {
      const refreshToken = Cookies.get('refresh_token');
      if (refreshToken) {
        try {
          const refreshResponse = await axios.post(URL_API + URL_REFRESH_LOGIN, {}, {
            headers: {
              Authorization: `Bearer ${refreshToken}`
            }
          });
          const newToken = refreshResponse.data.access_token;
          Cookies.set('token', newToken);
          return true;
        } catch (refreshError) {
          console.error('Error refreshing token:', refreshError);
          return false;
        }
      }
    }
    console.error('Error checking auth:', error);
    return false;
  }
};