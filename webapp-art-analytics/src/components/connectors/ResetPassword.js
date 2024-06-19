import React, { useState } from 'react';
import HeaderWhite from "../landing_page/Header_white.js";
import axios from 'axios';
import { URL_API, URL_RESET_PASSWORD } from '../../utils/constants.js';
import '../../css/ResetPassword.css';

function ResetPassword({t}) {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');
    
    try {
      const response = await axios.post(URL_API + URL_RESET_PASSWORD, { email }, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      setMessage(response.data.message);
    } catch (error) {
      setError(t("landing_page.trial.errorglobal"));
    }
  };

  return (
    <div>
      <HeaderWhite t={t}/>
        <div className="reset-password-container">
        <h2>{t("landing_page.resetpassword.title")}</h2>
        <form onSubmit={handleSubmit}>
            <div className="form-group">
            <label>{t("overall.email")}:</label>
            <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={t("overall.email")}
                required
            />
            </div>
            <button type="submit" className="reset-password-button">{t("landing_page.resetpassword.sendlink")}</button>
        </form>
        {message && <p className="message">{message}</p>}
        {error && <p className="error">{error}</p>}
        </div>
    </div>
  );
}

export default ResetPassword;