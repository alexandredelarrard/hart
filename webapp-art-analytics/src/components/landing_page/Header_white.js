import React from "react";
import { COMPANY_NAME } from "../../utils/constants";
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { US, FR } from 'country-flag-icons/react/3x2';
import logo_blanc from '../../assets/logo_fond_blanc.jpg';
import '../../css/Header.css';

const HeaderWhite = ({t}) => {

    const { i18n } = useTranslation();

    const changeLanguage = (lng) => {
        i18n.changeLanguage(lng);
    };

    return (
      <div className="firm-presentation">
        <header className="navbar-scrolled">
            <div className="logo-container">
                <a href="/" className="logo">
                    <img src={logo_blanc} alt="Firm Logo" className="firm-logo"/>
                </a>
                <span className="company-name">{COMPANY_NAME}</span>
            </div>
            <div className="menu-container-plateforme">
                <div className="language-container">
                    <button className="menu-item-plateforme lang-button" onClick={() => changeLanguage('en')}>
                        <US title="English Translation" className="flag-icon" />
                        English
                    </button>
                    <button className="menu-item-plateforme lang-button" onClick={() => changeLanguage('fr')}>
                        <FR title="Traduction en français" className="flag-icon" />
                        Français
                    </button>
                </div>
                <Link to="/login">
                    <button className="account-button">{t("landing_page.header.myaccount")}</button>
                </Link>
            </div>
        </header>
    </div>);
}
export default HeaderWhite;