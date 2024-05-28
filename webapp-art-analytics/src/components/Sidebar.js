import React, { useState } from 'react';
import axios from 'axios';
import {URL_API, URL_UPLOAD} from '../utils/constants';
import { useNavigate } from 'react-router-dom';

import '../css/Sidebar.css';

function Sidebar({ onSubmit }) {
  const [file, setFile] = useState(null);
  const [text, setText] = useState('');
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleTextChange = (e) => {
    setText(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    if (file) {
      formData.append('file', file);
    }
    if (text) {
      formData.append('text', text);
    }
    try {
      const response = await axios.post(URL_API + URL_UPLOAD, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      navigate('/', { state: { data: response.data, file, text } });
      onSubmit(file, text);
    } catch (error) {
      console.error('Error uploading file', error);
    }
  };

  return (
    <aside className="sidebar">
      <h3>Options</h3>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Load a picture:</label>
          <input type="file" onChange={handleFileChange} />
        </div>
        <div className="form-group">
          <label>Fill in text:</label>
          <textarea value={text} onChange={handleTextChange} placeholder="Enter text" />
        </div>
        <button type="submit" className="send-button">Send for Analysis</button>
      </form>
    </aside>
  );
}

export default Sidebar;