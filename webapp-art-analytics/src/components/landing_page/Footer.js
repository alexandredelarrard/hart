import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCopyright, faEnvelope } from '@fortawesome/free-solid-svg-icons';
import { faLinkedin, faInstagram, faTwitter } from '@fortawesome/free-brands-svg-icons';

// import useLogActivity from '../../hooks/general/useLogActivity.js';
import {validateEmail} from '../../utils/general.js';
import axiosInstance_middle from '../../hooks/general/axiosInstance';
import { COMPANY_NAME, URL_ADD_TO_NEWSLETTER } from "../../utils/constants";
import '../../css/Footer.css';

const Footer = ({t}) => {

    // const LogActivity = useLogActivity();
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        setMessage(''); // Clear any previous error
        e.preventDefault();

        if (!validateEmail(email)) {
            setError(t("landing_page.trial.erroremail"));
          } else {
            try {
                const response = await axiosInstance_middle.post(URL_ADD_TO_NEWSLETTER, {
                    'email': email
                },{
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                if(response.status === 200){
                    // await LogActivity("add_to_newsletter", email)
                    setMessage(t("landing_page.footer.addedtothelist"));
                }
            } catch (error) {
                if (error.response && error.response.status === 401) {
                    setError(t("landing_page.trial.error401"));
                  } else if (error.response && error.response.status === 404) {
                    setError(t("landing_page.trial.erroremailused"));
                  } else {
                    setError(t("landing_page.trial.errorglobal"));
                  }
            }
          }
      };

    return (
        <footer className="footer-section">
            <hr className="footer-separator" />
            <div className="footer-container">
                <div className="footer-column">
                    <form className="newsletter-form" onSubmit={handleSubmit}>
                        <h4>Newsletter</h4>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => {setEmail(e.target.value); setMessage(''); setError('')}}
                            placeholder={t("overall.email")}
                        />
                        {message && <p style={{ color: 'green' }}>{message}</p>}
                        {error && <p style={{ color: 'red' }}>{error}</p>}
                        <button type="submit" className="login-button">
                            <FontAwesomeIcon icon={faEnvelope} />
                        </button>
                    </form>
                </div>
                <div className="footer-column">
                    <div className="footer-company-info">
                        <FontAwesomeIcon icon={faCopyright} />
                        <div>
                            <span>Artycs 2024</span>
                        </div>
                    </div>
                    <div className="footer-social-links">
                        <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer">
                            <FontAwesomeIcon icon={faLinkedin} />
                        </a>
                        <a href="https://instagram.com" target="_blank" rel="noopener noreferrer">
                            <FontAwesomeIcon icon={faInstagram} />
                        </a>
                        <a href="https://twitter.com" target="_blank" rel="noopener noreferrer">
                            <FontAwesomeIcon icon={faTwitter} />
                        </a>
                    </div>

                </div>
                <div className="footer-column">
                    <h3>{t("landing_page.footer.producttitle")}</h3>
                    <a href="#product_1">{t("landing_page.footer.search")}</a>
                    <a href="#product_2">{t("landing_page.footer.estimate")}</a>
                    <a href="#product_3">{t("landing_page.footer.optimize")}</a>
                    <a href="#product_4">{t("landing_page.footer.authentification")}</a>
                    <a href="#pricing">{t("landing_page.footer.offers")}</a>
                    <Link to="/terms">{t("landing_page.footer.legal")}</Link>
                </div>
                <div className="footer-column">
                    <h3>{COMPANY_NAME}</h3>
                    <Link to="/about">{t("landing_page.footer.about").replace("{COMPANY_NAME}", COMPANY_NAME)}</Link>
                    <Link to="/contact">{t("overall.contactus")}</Link>
                    <Link to="/team">{t("landing_page.footer.team")}</Link>
                    {/* <Link to="/career">Career</Link> */}
                </div>
                <div className="footer-column">
                    <h3>{t("landing_page.footer.community")}</h3>
                    <Link to="/reviews">{t("landing_page.footer.reviews")}</Link>
                    <Link to="/blog">{t("landing_page.footer.blog")}</Link>
                    {/* <Link to="/external-links">{t("landing_page.footer.references")}</Link> */}
                </div>
            </div>
        </footer>
    );
}

export default Footer;
