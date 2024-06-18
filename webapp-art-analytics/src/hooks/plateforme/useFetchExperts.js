import { useEffect } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import { checkAuth } from '../general/identification';
import { useNavigate } from "react-router-dom";
import { URL_API, URL_GET_EXPERTS } from '../../utils/constants';

const useFetchExperts = (setExperts) => {
    const navigate = useNavigate();

    useEffect(() => {
        const fetchExperts = async () => {
            const token = Cookies.get('token');
            const checkUserAuth = async () => {
            const isAuthenticated = await checkAuth();
            if (!isAuthenticated) {
                navigate('/login'); // Redirect to the login page or home page if not authenticated
            }
            };

            checkUserAuth()

            const geolocation = Cookies.get('geolocation');
            if (geolocation) {
                const parsedGeolocation = JSON.parse(geolocation);
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
        };
        fetchExperts();
    }, [setExperts, navigate]);
};

export default useFetchExperts;
