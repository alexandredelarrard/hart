import { useEffect } from 'react';
import axiosInstance_back from '../general/axiosInstanceBack';
import { checkAuth } from '../general/identification';
import { useNavigate } from 'react-router-dom';
import { URL_GET_CHATBOT } from '../../utils/constants';

const useLLMDesignation = (taskId, additionalData, setNewResultSaved, chatBotResultFetched, setBotResult, setChatBotResultFetched) => {
    const navigate = useNavigate();
    useEffect(() => {
        if (taskId && additionalData.length !==0 && !chatBotResultFetched) {
            const fetchLLM = async () => {
                try {
                const art_pieces = additionalData.map(item => ({
                    "description": item.description,
                    "distance": item.distance
                }));

                const response = await axiosInstance_back.post(URL_GET_CHATBOT, 
                    { "art_pieces": art_pieces,
                    "task_id": taskId
                    },{
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
                
                setBotResult(response.data.result)
                setChatBotResultFetched(true);
                setNewResultSaved(true);

                } catch (error) {
                console.error('Error fetching additional data', error);
                }
            };

            const isAuthenticated = checkAuth();
            if (isAuthenticated){
                fetchLLM();
            } else {
                navigate('/login');
            }
        }
    }, [taskId, additionalData, setNewResultSaved, chatBotResultFetched, setBotResult, setChatBotResultFetched]);

};

export default useLLMDesignation;