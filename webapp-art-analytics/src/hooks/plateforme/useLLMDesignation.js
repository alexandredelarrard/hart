import { useEffect } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import { URL_API_BACK } from '../../utils/constants';

const useLLMDesignation = (taskId, additionalData, setNewResultSaved, chatBotResultFetched, setBotResult, setChatBotResultFetched) => {
    useEffect(() => {
        if (taskId && additionalData.length !==0 && !chatBotResultFetched) {

        const fetchLLM = async () => {
            try {
            const token = Cookies.get('token');
            if (!token) {
                return;
            }

            const art_pieces = additionalData.map(item => ({
                "description": item.description,
                "distance": item.distance
              }));

            const response = await axios.post(URL_API_BACK + '/chatbot', 
                { "art_pieces": art_pieces,
                  "task_id": taskId
                 },{
                headers: {
                    Authorization: `Bearer ${token}`,
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
        fetchLLM();
        }
    }, [taskId, additionalData, setNewResultSaved, chatBotResultFetched, setBotResult, setChatBotResultFetched]);

};

export default useLLMDesignation;