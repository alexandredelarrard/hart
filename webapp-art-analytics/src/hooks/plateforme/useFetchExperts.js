import { useEffect } from 'react';
import axiosInstance_middle from '../general/axiosInstance';
import Cookies from 'js-cookie';
import { useNavigate } from 'react-router-dom';
import { checkAuth} from '../general/identification';
import { URL_GET_EXPERTS } from '../../utils/constants';

const useFetchExperts = (setExperts) => {
    const navigate = useNavigate();

    useEffect(() => {
        const fetchExperts = async () => {
            const isAuthenticated = await checkAuth();
            const geolocation = Cookies.get('geolocation');
            if(isAuthenticated){
                if (geolocation) {
                    const parsedGeolocation = JSON.parse(geolocation);
                    try {
                        const response = await axiosInstance_middle.post(URL_GET_EXPERTS, {
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
                navigate("/login");
            }
        };
        fetchExperts();
    }, [setExperts]);
};

export default useFetchExperts;
