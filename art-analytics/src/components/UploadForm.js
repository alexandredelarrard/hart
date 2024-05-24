import React from 'react';
import '../css/UploadForm.css';

function UploadForm({ file, text, submitted }) {

  return (
    <div className="upload-form-container">
      {!submitted ? (
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
        </div>
      )}
    </div>
  );
}

export default UploadForm;