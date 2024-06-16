import React, { useState, useEffect } from 'react';
import HeaderWhite from "./landing_page/Header_white.js";
import { useNavigate } from 'react-router-dom';
import { logActivity } from '../utils/activity.js';
import axios from 'axios';
import Cookies from 'js-cookie';
import {URL_API, URL_LOGIN} from '../utils/constants';
import LoginElement from './LoginElement.js';
import '../css/Login.css';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    setError(''); // Clear any previous error
    e.preventDefault();
    try {
      const response = await axios.post(URL_API + URL_LOGIN, { email, password }, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      // Save token to localStorage and redirect to upload page
      Cookies.set('token', response.data.access_token, { expires: 0.5 });
      Cookies.set('refresh_token', response.data.refresh_token, { expires: 0.5 });
      Cookies.set('userdata', JSON.stringify(response.data.userdata), { expires: 0.5 });

      // log activity 
      logActivity("click_log_in", "")

      setMessage(response.data.message);
      navigate('/analytics');
    } catch (error) {
      if (error.response && error.response.status === 401) {
        setError('Invalid email or password');
      } else if (error.response && error.response.status === 404) {
        setError('Email not found');
      } else {
        setError('An error occurred. Please try again later.');
      }
    }
  };

  useEffect(() => {
    const token = Cookies.get('token');
    const userdata = Cookies.get('userdata');
    if (token && userdata) {
      navigate('/analytics');
    }
  }, [navigate]);

  return (
    <div>
      <HeaderWhite/>
      <div className="login-container">
        <LoginElement
          handleSubmit={handleSubmit}
          email={email}
          password={password}
          error={error}
          message={message}
          setEmail={setEmail}
          setPassword={setPassword}
        />
      </div>
    </div>
  );
}

export default Login;