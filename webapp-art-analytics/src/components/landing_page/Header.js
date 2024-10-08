import React, { useState } from "react";
import { COMPANY_NAME, PATHS } from "../../utils/constants";
import Cookies from 'js-cookie';
import { Link } from 'react-router-dom';
import { US, FR } from 'country-flag-icons/react/3x2';
import logo from '../../assets/logo.jpg';
import logo_blanc from '../../assets/logo_fond_blanc.jpg';

import '../../css/Header.css';

const Header = ({ t, changeLanguage, scrolled }) => {

    const [menuOpen, setMenuOpen] = useState(false);
    const token = Cookies.get("token");

    return (
        <div className="firm-presentation">
            <header className={`${scrolled ? "navbar white-background" : "navbar"} ${menuOpen ? "show-menu" : ""}`}>
                <div className="logo-container">
                    <a href={PATHS["HOME"]} className="logo">
                        <img src={scrolled ? logo_blanc : logo} alt="Firm Logo" className="firm-logo" />
                    </a>
                    <span className={`company-name ${scrolled ? "company-name-scrolled" : ""}`}>{COMPANY_NAME}</span>
                    <div className="menu-toggle" onClick={() => setMenuOpen(!menuOpen)}>
                        ☰
                    </div>
                </div>
                <div className={`menu-header ${ menuOpen ? "menu-content show": "menu-content"}`}>
                    <nav className="nav-links">
                        <a href={PATHS["HOME_PRODUCT"]}>{t("landing_page.header.products")}</a>
                        <a href={PATHS["HOME_PRICING"]}>{t("landing_page.header.offers")}</a>
                        {/* <a href={PATHS["BLOG"]}>{t("landing_page.header.blog")}</a> */}
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
                        <Link to={PATHS["LOGIN"]}>
                            <button className="account-button">{token ? t("landing_page.header.myaccount") : t("landing_page.header.login")}</button>
                        </Link>
                    </div>
                </div>
            </header>
        </div>
    );
}
export default Header;
