import { useEffect } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import { URL_API, URL_GET_EXPERTS } from '../../utils/constants';

const useFetchExperts = (setExperts) => {

    useEffect(() => {
        const fetchExperts = async () => {
        const token = Cookies.get('token');
        if (!token) {
            return;
        }

        const geolocation = Cookies.get('geolocation');
        if (geolocation) {
            const parsedGeolocation = JSON.parse(geolocation);
            console.log()
            try {
                const response = await axios.post(URL_API + URL_GET_EXPERTS, {
                    'longitude': parsedGeolocation.longitude,
                    'latitude': parsedGeolocation.latitude,
                    },{
                    headers: {
                        Authorization: `Bearer ${token}`,
                        'Content-Type': 'application/json',
                    },
                });
                
                // Ensure response.data is an array
                if (Array.isArray(response.data.result)) {
                    setExperts(response.data.result);
                } else {
                    console.error('Unexpected response format:', response.data);
                }
            } catch (error) {
                console.error('Error fetching experts:', error);
            }
        }
        };
        fetchExperts();
  }, [setExperts]);
};

export default useFetchExperts;
