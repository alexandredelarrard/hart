import { useState, useEffect } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import { logActivity } from '../../../utils/activity';
import { URL_API_BACK, URL_UPLOAD } from '../../../utils/constants';

const useUploadHandler = ({ file, text, setFile, setText, setTaskId, setResult, setBotResult, setChatBotResultFetched, setAnalysisInProgress, setAdditionalData, setAvgMinEstimates, setAvgMaxEstimates, setAvgFinalResult, setNewResultSaved }) => {
  const [fileUrl, setFileUrl] = useState(null);

  const handleSearchFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSearchTextChange = (e) => {
    setText(e.target.value);
  };

  const handleSearchSubmit = async (e) => {
    e.preventDefault();
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
        logActivity("click_search_submit", "file_and_text")}
      else if(file){
        logActivity("click_search_submit", "file")
      } else {
        logActivity("click_search_submit", "text")
      }

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