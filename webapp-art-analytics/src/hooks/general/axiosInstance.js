import axios from 'axios';
import Cookies from 'js-cookie';
import { URL_API, URL_REFRESH_LOGIN, PATHS } from '../../utils/constants';

const axiosInstance_middle = axios.create({
  baseURL: URL_API,
});

// Request interceptor to add the token to headers
axiosInstance_middle.interceptors.request.use(
  (config) => {
    const token = Cookies.get('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh and redirection on 401 errors
axiosInstance_middle.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
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
          originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
          return axiosInstance_middle(originalRequest);
        } catch (refreshError) {

          console.log('Error refreshing token:', refreshError);
          Cookies.remove('token');
          Cookies.remove('refresh_token');
          Cookies.remove('userdata');
          Cookies.remove('plan_name');
          Cookies.remove('plan_end_date');
          Cookies.remove('remaining_closest_volume');
          Cookies.remove('remaining_search_volume');

          window.location.href = PATHS["LOGIN"];
          return Promise.reject(refreshError);
        }
      } else {
        Cookies.remove('token');
        Cookies.remove('refresh_token');
        Cookies.remove('userdata');
        Cookies.remove('plan_name');
        Cookies.remove('plan_end_date');
        Cookies.remove('remaining_closest_volume');
        Cookies.remove('remaining_search_volume');

        window.location.href = PATHS["LOGIN"];
        return Promise.reject(error);
      }
    }
    return Promise.reject(error);
  }
);

export default axiosInstance_middle;
