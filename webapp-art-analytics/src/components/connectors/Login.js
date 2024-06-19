import React, { useState, useEffect } from 'react';
import HeaderWhite from "../landing_page/Header_white.js";
import { useNavigate } from 'react-router-dom';
import useLogActivity from '../../hooks/general/useLogActivity.js';
import {login, checkAuth} from '../../hooks/general/identification.js';
import LoginElement from './LoginElement.js';
import '../../css/Login.css';

function Login({t}) {
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
        setError(t("landing_page.trial.error401"));
      } else if (error.response && error.response.status === 404) {
        setError(t("landing_page.trial.erroremailnotfound"));
      } else {
        setError(t("landing_page.trial.errorglobal"));
      }
    }
  };

  useEffect(() => {
    const checkUserAuth = async () => {
      const isAuthenticated = await checkAuth();
      if (isAuthenticated) {
          navigate('/analytics');
      }
    };

    checkUserAuth()
  }, [navigate]);

  return (
    <div>
      <HeaderWhite t={t}/>
      <div className="login-container">
        <LoginElement
          handleSubmit={handleSubmit}
          email={email}
          password={password}
          error={error}
          message={message}
          setEmail={setEmail}
          setPassword={setPassword}
          t={t}
        />
      </div>
    </div>
  );
}

export default Login;