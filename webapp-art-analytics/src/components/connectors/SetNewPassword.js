import React, { useState } from 'react';
import Header from "../landing_page/Header.js";
import axios from 'axios';
import { useNavigate, useParams } from 'react-router-dom';
import { URL_API, URL_SET_NEW_PASSWORD, PATHS } from '../../utils/constants.js';

import '../../css/SetNewPassword.css';

function SetNewPassword({changeLanguage, t}) {
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
      navigate(PATHS["LOGIN"]);
    } catch (error) {
      setError(t("landing_page.trial.errorglobal"));
    }
  };

  return (
    <div>
      <Header changeLanguage={changeLanguage} scrolled={true} t={t}/>
      <div className="set-new-password-container">
        <h2>{t("landing_page.setnewpassword.title")}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>{t("overall.password")}:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={t("landing_page.setnewpassword.enternewpassword")}
              required
            />
          </div>
          <button type="submit" className="set-new-password-button">{t("landing_page.setnewpassword.newpasswordsend")}</button>
        </form>
        {message && <p className="message">{message}</p>}
        {error && <p className="error">{error}</p>}
      </div>
    </div>
  );
}

export default SetNewPassword;
