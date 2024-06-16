import React, { useState } from 'react';
import HeaderWhite from "../landing_page/Header_white.js";
import axios from 'axios';
import { useNavigate, useParams } from 'react-router-dom';
import { URL_API, URL_SET_NEW_PASSWORD } from '../../utils/constants.js';
import '../../css/SetNewPassword.css';

function SetNewPassword() {
  const { token } = useParams();
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${URL_API}${URL_SET_NEW_PASSWORD}/${token}`, { token, password }, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      setMessage(response.data.message);
      navigate('/login');
    } catch (error) {
      setError('An error occurred. Please try again later.');
    }
  };

  return (
    <div>
      <HeaderWhite/>
      <div className="set-new-password-container">
        <h2>Set New Password</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>New Password:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your new password"
              required
            />
          </div>
          <button type="submit" className="set-new-password-button">Set New Password</button>
        </form>
        {message && <p className="message">{message}</p>}
        {error && <p className="error">{error}</p>}
      </div>
    </div>
  );
}

export default SetNewPassword;