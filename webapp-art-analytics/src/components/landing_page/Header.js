import React, { useEffect, useState } from "react";
import { COMPANY_NAME } from "../../utils/constants";
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { US, FR } from 'country-flag-icons/react/3x2';
import logo from '../../assets/logo.jpg';
import logo_blanc from '../../assets/logo_fond_blanc.jpg';
import '../../css/Header.css';

const Header = ({t}) => {
    const [scrolled, setScrolled] = useState(false);
    const { i18n } = useTranslation();

    const changeLanguage = (lng) => {
        i18n.changeLanguage(lng);
    };

    useEffect(() => {
        const handleScroll = () => {
        setScrolled(window.scrollY > 0);
        };

        window.addEventListener("scroll", handleScroll);
        return () => {
        window.removeEventListener("scroll", handleScroll);
        };
    }, []);

    return (
      <div className="firm-presentation">
        <header className={`${scrolled ? "navbar-scrolled" : "navbar"}`}>
            <div className="logo-container">
                <a href="/" className="logo">
                    <img src={scrolled ? logo_blanc: logo} alt="Firm Logo" className="firm-logo"/>
                </a>
                <span className={`company-name ${scrolled ? "company-name-scrolled" : ""}`}>{COMPANY_NAME}</span>
            </div>
            <nav className="nav-links">
                <a href="#product">{t("landing_page.header.products")}</a>
                <a href="#pricing">{t("landing_page.header.offers")}</a>
                <a href="#blog">{t("landing_page.header.blog")}</a>
            </nav>
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
export default Header;