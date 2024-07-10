import axiosInstance_middle from '../general/axiosInstance';
import { checkAuth } from '../general/identification';
import { URL_UPDATE_PROFILE, PATHS } from '../../utils/constants';

export const ModifyProfile = async (name, surname, address) => {
    const isAuthenticated = await checkAuth();

    if (isAuthenticated) {
      try {
        const response = await axiosInstance_middle.post(URL_UPDATE_PROFILE, { name, surname, address });
        return response.data;
      } catch (error) {
        console.error('Error updating user data', error);
        throw error;
      }
    } else {
      window.location.href = PATHS["LOGIN"];
      throw new Error('User not authenticated');
    }
  };
