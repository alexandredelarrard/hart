import axios from 'axios';
import Cookies from 'js-cookie';
import { URL_API_BACK } from '../../utils/constants';

// Create an Axios instance
const axiosInstance_back = axios.create({
  baseURL: URL_API_BACK,
});

// Request interceptor to add the token to headers
axiosInstance_back.interceptors.request.use(
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

export default axiosInstance_back;