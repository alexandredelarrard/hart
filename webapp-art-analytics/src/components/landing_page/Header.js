import React, { useState } from "react";
import { COMPANY_NAME } from "../../utils/constants";
import { Link } from 'react-router-dom';
import { US, FR } from 'country-flag-icons/react/3x2';
import logo from '../../assets/logo.jpg';
import logo_blanc from '../../assets/logo_fond_blanc.jpg';
import '../../css/Header.css';

const Header = ({ t, changeLanguage, scrolled }) => {
    
    const [menuOpen, setMenuOpen] = useState(false);

    return (
        <div className="firm-presentation">
            <header className={`${scrolled ? "navbar white-background" : "navbar"} ${menuOpen ? "show-menu" : ""}`}>
                <div className="logo-container">
                    <a href="/" className="logo">
                        <img src={scrolled ? logo_blanc : logo} alt="Firm Logo" className="firm-logo" />
                    </a>
                    <span className={`company-name ${scrolled ? "company-name-scrolled" : ""}`}>{COMPANY_NAME}</span>
                    <div className="menu-toggle" onClick={() => setMenuOpen(!menuOpen)}>
                        ☰
                    </div>
                </div>
                <div className={`menu-header ${ menuOpen ? "menu-content show": "menu-content"}`}>
                    <nav className="nav-links">
                        <a href="/#product">{t("landing_page.header.products")}</a>
                        <a href="/#pricing">{t("landing_page.header.offers")}</a>
                        <a href="/blog">{t("landing_page.header.blog")}</a>
                    </nav>
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
                    <div className="menu-container">
                        <Link to="/login">
                            <button className="account-button">{t("landing_page.header.myaccount")}</button>
                        </Link>
                    </div>
                </div>
            </header>
        </div>
    );
}
export default Header;