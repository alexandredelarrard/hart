import React from "react";
import { COMPANY_NAME } from "../../utils/constants";
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCopyright, faEnvelope } from '@fortawesome/free-solid-svg-icons';
import { faLinkedin, faInstagram, faTwitter } from '@fortawesome/free-brands-svg-icons';
import '../../css/Footer.css';

const Footer = ({t}) => {
    return (
        <footer className="footer-section">
            <hr className="footer-separator" />
            <div className="footer-container">
                <div className="footer-column">
                    <form className="newsletter-form">
                        <h4>Newsletter</h4>
                        <input type="email" placeholder={t("overall.email")} />
                        <button type="submit">
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