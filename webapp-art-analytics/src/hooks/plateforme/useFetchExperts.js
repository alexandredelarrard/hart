import { useEffect } from 'react';
import axiosInstance_middle from '../general/axiosInstance';
import Cookies from 'js-cookie';
import { checkAuth} from '../general/identification';
import { URL_GET_EXPERTS, PATHS} from '../../utils/constants';

const useFetchExperts = (setExperts) => {
    useEffect(() => {
        const isAuthenticated = checkAuth();
        if(isAuthenticated){
            const geolocation = Cookies.get('geolocation');
            if (geolocation) {
                const parsedGeolocation = JSON.parse(geolocation);
                try {
                    const response = axiosInstance_middle.post(URL_GET_EXPERTS, {
                        'longitude': parsedGeolocation.longitude,
                        'latitude': parsedGeolocation.latitude,
                    },{
                        headers: {
                            'Content-Type': 'application/json',
                        },
                    });
                    // Ensure response.data is an array
                    if (Array.isArray(response.data.result)) {
                        if (typeof setExperts === 'function') {
                            setExperts(response.data.result);
                        } else {
                            console.error('setExperts is not a function:', setExperts);
                        }
                    } else {
                        console.error('Unexpected response format:', response.data);
                    }
                } catch (error) {
                    console.error('Error fetching experts:', error);
                }
            }
        } else {
            window.location.href = PATHS["LOGIN"];
        }
    }, [setExperts]);
};

export default useFetchExperts;
