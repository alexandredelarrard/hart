import React, { useState } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import { Link } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import {URL_API, URL_SIGNIN, PATHS} from '../../utils/constants';
import {validateEmail, validatePassword} from '../../utils/general.js';
import Header from "../landing_page/Header.js";

import '../../css/Trial.css';

const Trial = () => {
    const { t } = useTranslation();
    const [email, setEmail] = useState('');
    const [emailError, setEmailError] = useState('');
    const [password, setPassword] = useState('');
    const [passwordError, setPasswordError] = useState('');
    const [username, setUsername] = useState('');
    const [surname, setSurname] = useState('');
    const [metier, setMetier] = useState('');
    const [otherJob, setOtherJob] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();



    const handlePasswordChange = (e) => {
        const newPassword = e.target.value;
        setPassword(newPassword);
        if (!validatePassword(newPassword)) {
          setPasswordError(t("landing_page.trial.errorpassword"));
        } else {
          setPasswordError('');
        }
    };

    const handleEmailChange = (e) => {
        const newEmail = e.target.value;
        setEmail(newEmail);
        if (!validateEmail(newEmail)) {
          setEmailError(t("landing_page.trial.erroremail"));
        } else {
          setEmailError('');
        }
      };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(''); // Clear any previous error

        const jobTitle = metier === 'other' ? otherJob : metier;

        try {
          const response = await axios.post(`${URL_API}${URL_SIGNIN}`, {
            "surname": surname,
            "username": username,
            "email": email,
            "password": password,
            metier: jobTitle }, {
            headers: {
              'Content-Type': 'application/json',
            },
          });

          // Save token to cookies and redirect to analytics
          Cookies.set('token', response.data.access_token, { expires: 0.5 });
          Cookies.set('userdata', JSON.stringify(response.data.userdata), { expires: 0.5 });
          setMessage(response.data.message);
          navigate(PATHS["ANALYTICS"]);
        } catch (error) {
          if (error.response && error.response.status === 401) {
            setError(t("landing_page.trial.error401"));
          } else if (error.response && error.response.status === 404) {
            setError(t("landing_page.trial.erroremailused"));
          } else {
            setError(t("landing_page.trial.errorglobal"));
          }
        }
      };

    return (
      <div>
        <Header scrolled={true} t={t}/>
        <div className="trial-container">
            <section className="trial-form-section">
                <h2>{t("landing_page.trial.trialtitle")}</h2>
                <form className="trial-form"  onSubmit={handleSubmit}>
                    <div className="form-row">
                        <div className="form-group">
                            <label>{t("overall.surname")}</label>
                            <input
                                type="text"
                                value={surname}
                                placeholder={t("overall.surname")}
                                onChange={(e) => setSurname(e.target.value)}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label>{t("overall.name")}</label>
                            <input
                                type="text"
                                value={username}
                                placeholder={t("overall.name")}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                            />
                        </div>
                    </div>
                    <div className="form-group">
                        <label>{t("landing_page.trial.emailpro")}</label>
                        <input
                            type="email"
                            value={email}
                            onChange={handleEmailChange}
                            placeholder={t("overall.email")}
                            required
                        />
                        {emailError && <p style={{ color: 'red' }}>{emailError}</p>}
                    </div>
                    <div className="form-group">
                        <label>{t("landing_page.trial.passwordtitle")}</label>
                        <input
                            type="password"
                            value={password}
                            onChange={handlePasswordChange}
                            placeholder={t("overall.password")}
                            required
                        />
                        {passwordError && <p style={{ color: 'red' }}>{passwordError}</p>}
                    </div>
                    <div className="form-group">
                        <label>Métier</label>
                        <select
                            value={metier}
                            onChange={(e) => setMetier(e.target.value)}
                            required>
                                <option value="">{t("landing_page.trial.selectoption")}</option>
                                <option value="independent">{t("landing_page.trial.optionindependent")}</option>
                                <option value="expert">{t("landing_page.trial.optionexpert")}</option>
                                <option value="commissaire">{t("landing_page.trial.optioncommissaire")}</option>
                                <option value="insurance">{t("landing_page.trial.optioninsurer")}</option>
                                <option value="student">{t("landing_page.trial.optionstudent")}</option>
                                <option value="other">{t("landing_page.trial.otheroption")}</option>
                        </select>
                    </div>
                    {metier === 'other' && (
                    <div className="form-group">
                        <label>{t("landing_page.trial.otherjobtitle")}</label>
                        <input
                            type="text"
                            value={otherJob}
                            placeholder={t("landing_page.trial.otherjobplaceholder")}
                            onChange={(e) => setOtherJob(e.target.value)}
                            required
                        />
                    </div>
                    )}
                    <div className="form-group checkbox-group">
                        <label>
                            <p>{t("landing_page.trial.explanationwhycollect")}</p>
                            <div className="checkbox-container">
                                <input type="checkbox" required />
                                <span>
                                {t("landing_page.trial.accept")}<Link to="/terms">{t("landing_page.trial.cgu")}</Link>{t("landing_page.trial.and")}<Link to="/cgv">{t("landing_page.trial.cgv")}</Link>.
                                </span>
                            </div>
                        </label>
                    </div>
                    <button type="submit" className="login-button" disabled={passwordError || emailError}>{t("overall.starttrial")}</button>
                </form>
                {message && <p className="message">{message}</p>}
                {error && <p className="error">{error}</p>}
                <hr className="login-delimiter" />
                <div className='login-trial'>
                    <p>{t("overall.alreadyenrolled")} <Link to={PATHS["LOGIN"]}>{t("overall.pleaseconnect")}</Link>.</p>
                </div>
            </section>
        </div>
      </div>
    );
}

export default Trial;
