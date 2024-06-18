import { useState, useEffect } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import useLogActivity from '../general/useLogActivity';
import { URL_API_BACK, URL_UPLOAD } from '../../utils/constants';

const useUploadHandler = ({ file, text, setFile, setText, setTaskId, setResult, setBotResult, setChatBotResultFetched, setAnalysisInProgress, setAdditionalData, setAvgMinEstimates, setAvgMaxEstimates, setAvgFinalResult, setNewResultSaved }) => {
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
    const token = Cookies.get('token');
    if (!token) {
      return;
    }
    
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
      const response = await axios.post(URL_API_BACK + URL_UPLOAD, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
           Authorization: `Bearer ${token}`
        },
      });

      setFile(file);
      setText(text);
      setBotResult(null)
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

export default useUploadHandler;