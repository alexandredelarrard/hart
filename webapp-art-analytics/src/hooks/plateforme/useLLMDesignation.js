import { useEffect, useRef } from 'react';
import axiosInstance_back from '../general/axiosInstanceBack';
import { checkAuth } from '../general/identification';
import { URL_GET_CHATBOT } from '../../utils/constants';

const useLLMDesignation = (taskId, additionalData, setNewResultSaved, chatBotResultFetched, setBotResult, setChatBotResultFetched) => {

    const setNewResultSavedRef = useRef(setNewResultSaved);
    const setBotResultRef = useRef(setBotResult);
    const setChatBotResultFetchedRef = useRef(setChatBotResultFetched);

    useEffect(() => {
        setNewResultSavedRef.current = setNewResultSaved;
        setBotResultRef.current = setBotResult;
        setChatBotResultFetchedRef.current = setChatBotResultFetched;
    }, [setNewResultSaved, setBotResult, setChatBotResultFetched]);

    useEffect(() => {
        if (taskId && additionalData.length !== 0 && !chatBotResultFetched) {
            const fetchLLM = async () => {
                try {
                    const art_pieces = additionalData.map(item => ({
                        "description": item.description,
                        "distance": item.distance
                    }));

                    const response = await axiosInstance_back.post(URL_GET_CHATBOT, {
                        "art_pieces": art_pieces,
                        "task_id": taskId
                    }, {
                        headers: {
                            'Content-Type': 'application/json',
                        },
                    });

                    setBotResultRef.current(response.data.result);
                    setChatBotResultFetchedRef.current(true);
                    setNewResultSavedRef.current(true);

                } catch (error) {
                    console.error('Error fetching additional data', error);
                }
            };

            const isAuthenticated = checkAuth();
            if (isAuthenticated) {
                fetchLLM();
            } else {
                window.location.href = "/login";
            }
        }
    }, [taskId, additionalData, chatBotResultFetched]);

};

export default useLLMDesignation;
