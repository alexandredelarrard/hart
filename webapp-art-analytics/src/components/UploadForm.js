import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../css/UploadForm.css';
import {URL_API_BACK, URL_GET_TASK} from '../utils/constants';

function UploadForm({ taskId, file, text }) {
  const [result, setResult] = useState(null);

  useEffect(() => {
    if (taskId) {
      const interval = setInterval(async () => {
        try {
          const response = await axios.get(URL_API_BACK + URL_GET_TASK + '/' + taskId);
          console.log(response)
          if (response.data.state === 'SUCCESS') {
            setResult(response.data.result);
            clearInterval(interval);
          }
        } catch (error) {
          console.error('Error fetching task result', error);
        }
      }, 1000); // Poll every X sec
      return () => clearInterval(interval);
    }
  }, [taskId]);

  return (
    <div className="upload-form-container">
      {!taskId ? (
        <div>
          <h2>Welcome to Art Analytics</h2>
          <p>Our solution provides detailed analysis of artwork through image and text inputs.</p>
        </div>
      ) : (
        <div className="result-container">
          <div className="image-container">
            {file && <img src={URL.createObjectURL(file)} alt="Uploaded" />}
          </div>
          <div className="text-container">
            {text && <p>{text}</p>}
          </div>
          {result && (
            <div className="analysis-result">
              <h3>Analysis Result</h3>
              <pre>{JSON.stringify(result, null, 2)}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default UploadForm;