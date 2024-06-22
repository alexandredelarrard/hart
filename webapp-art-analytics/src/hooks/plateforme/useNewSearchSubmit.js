import { useState, useEffect } from 'react';
import Cookies from 'js-cookie';

import axiosInstance_back from '../general/axiosInstanceBack';
import { checkAuth } from '../general/identification';
import useLogActivity from '../general/useLogActivity';
import { URL_UPLOAD } from '../../utils/constants';

const useNewSearchSubmit = ({ 
      file, 
      text, 
      setFile, 
      setText, 
      setTaskId, 
      setResult, 
      setBotResult, 
      setChatBotResultFetched, 
      setAnalysisInProgress, 
      setAdditionalData, 
      setAvgMinEstimates, 
      setAvgMaxEstimates, 
      setAvgFinalResult, 
      setNewResultSaved 
}) => {

  const [fileUrl, setFileUrl] = useState(null);
  const LogActivity = useLogActivity();

  const handleSearchFileChange = (e) => {
    setFile(e);
  };

  const handleSearchTextChange = (e) => {
    setText(e.target.value);
  };

  const handleSearchSubmit = async (e) => {
    e.preventDefault();
    const isAuthenticated = await checkAuth();

    if(isAuthenticated){
      
      const userdataString = Cookies.get("userdata");
      const formData = new FormData();
      if (file) {
        formData.append('file', file);
      }
      if (text) {
        formData.append('text', text);
      }
      formData.append('user_id', JSON.parse(userdataString).id);
      
      try {
        const response = await axiosInstance_back.post(URL_UPLOAD, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        setFile(file);
        setText(text);
        setBotResult(null);
        setChatBotResultFetched(false);
        setAnalysisInProgress(true);
        setTaskId(response.data.task_id);
        setResult(null);
        setAdditionalData([]);
        setAvgMinEstimates(0);
        setAvgMaxEstimates(0);
        setAvgFinalResult(0);
        setNewResultSaved(false);

        // log activity 
        if(file && text){
          LogActivity("click_search_submit", "file_and_text")}
        else if(file){
          LogActivity("click_search_submit", "file")
        } else {
          LogActivity("click_search_submit", "text")
        }

        // update the volume of search remaining 
        let remainingClosestVolume = Number(Cookies.get('remaining_closest_volume'));
        Cookies.set('remaining_closest_volume', remainingClosestVolume - 1);
      
      } catch (error) {
        console.error('Error uploading file', error);
      }
    } else {
      window.location.href = '/login';
    }
  };

  useEffect(() => {
    if (file) {
      const url = URL.createObjectURL(file);
      setFileUrl(url);

      // Cleanup function to revoke the object URL
      return () => URL.revokeObjectURL(url);
    }
  }, [file]);

  return {
    file,
    text,
    fileUrl,
    handleSearchFileChange,
    handleSearchTextChange,
    handleSearchSubmit,
  };
};

export default useNewSearchSubmit;