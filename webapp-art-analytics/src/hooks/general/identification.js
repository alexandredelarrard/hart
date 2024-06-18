import axios from 'axios';
import Cookies from 'js-cookie';
import { URL_API, URL_CHECK_LOGIN, URL_LOGIN, URL_LOGOUT, URL_REFRESH_LOGIN } from '../../utils/constants';

export const login = async (email, password) => {
  try {
    const response = await axios.post(URL_API + URL_LOGIN, { email, password }, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    if (response.status === 200) {
      // Save token to localStorage and redirect to upload page
      Cookies.set('token', response.data.access_token, { expires: 0.5 });
      Cookies.set('refresh_token', response.data.refresh_token, { expires: 15 });
      Cookies.set('userdata', JSON.stringify(response.data.userdata), { expires: 0.5 });
      Cookies.set('plan_name', response.data.plan_name, { expires: 0.5 });
      Cookies.set('plan_end_date', response.data.plan_end_date, { expires: 0.5 });
      Cookies.set('remaining_closest_volume', response.data.remaining_closest_volume, { expires: 0.5 });
      Cookies.set('remaining_search_volume', response.data.remaining_search_volume, { expires: 0.5 });

      return response;
    } else {
      console.error('Error backend:', response.status);
    }
  } catch (error) {
    console.error('Error logged in:', error);
}
}

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
      Cookies.remove('plan_name');
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