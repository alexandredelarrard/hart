import React, { useState, useEffect } from 'react';
import HeaderWhite from "../landing_page/Header_white.js";
import { useNavigate } from 'react-router-dom';
import useLogActivity from '../../hooks/general/useLogActivity.js';
import {login} from '../../hooks/general/identification.js';
import Cookies from 'js-cookie';
import LoginElement from './LoginElement.js';
import '../../css/Login.css';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const LogActivity = useLogActivity();

  const handleSubmit = async (e) => {
    setError(''); // Clear any previous error
    e.preventDefault();
    try {
      const response = await login(email, password);
      setMessage(response.data.message);
      
      // log activity 
      const success = await LogActivity("click_log_in", "")
      if (success) {
        navigate('/analytics');
      } else {
        console.log('Failed to log activity');
      }
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