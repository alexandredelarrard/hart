import React, { useState } from 'react';
import Header from "./landing_page/Header.js";
import Footer from "./landing_page/Footer.js";
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {URL_API, URL_LOGIN} from '../utils/constants';
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
      localStorage.setItem('token', response.data.access_token);
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

  return (
    <div>
      <Header />

      <div className="login-container">
        <div className="login-form">
          <h2>Login</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Email:</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                required
              />
            </div>
            <div className="form-group">
              <label>Password:</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
              />
            </div>
            <button type="submit" className="login-button">Login</button>
          </form>
          {message && <p className="message">{message}</p>}
          {error && <p className="error">{error}</p>}
        </div>
      </div>
    </div>
  );
}

export default Login;