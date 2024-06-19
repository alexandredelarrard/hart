import React from 'react';
import { Link } from 'react-router-dom';

function LoginElement({
    handleSubmit,
    email,
    password,
    error,
    message,
    setEmail,
    setPassword,
    t
}) {
 
  return (
        <div className="login-form">
          <h2>{t("landing_page.login.title")}</h2>
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
            <div className="form-group">
              <label>{t("overall.password")}:</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={t("overall.password")}
                required
              />
            </div>
            <button type="submit" className="login-button">{t("landing_page.login.loginbutton")}</button>
          </form>
          {message && <p className="message">{message}</p>}
          {error && <p className="error">{error}</p>}
          <hr className="login-delimiter" />
          <div className='login-trial'>
            <p><Link to="/reset-password">{t("landing_page.login.forgottenpassword")}</Link> | {t("landing_page.login.notyetenrolled")} <Link to="/trial">{t("overall.starttrial")}</Link></p>
          </div>
        </div>
  );
}

export default LoginElement;