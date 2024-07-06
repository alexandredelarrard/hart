import React, { useState } from "react";
import { COMPANY_NAME } from "../../../utils/constants";
import logo_blanc from '../../../assets/logo_fond_blanc.jpg';
import { US, FR } from 'country-flag-icons/react/3x2';
import '../../../css/HeaderPlateforme.css';

const HeaderPlateforme = ({t, changeLanguage, handleMenuClick }) => {

    const [menuOpen, setMenuOpen] = useState(false);

    return (
        <div className="firm-presentation-plateforme">
            <header className="navbar-scrolled-plateforme">
                <div className="logo-container-plateforme">
                    <a href="/" className="logo-plateforme">
                        <img src={logo_blanc} alt="Firm Logo" className="firm-logo" />
                    </a>
                    <span className="company-name-plateforme">{COMPANY_NAME}</span>
                    <div className="menu-toggle" onClick={() => setMenuOpen(!menuOpen)}>
                        ☰
                    </div>
                </div>
                <div className="menu-container-plateforme">
                    <div className={`menu-header ${ menuOpen ? "menu-content show": "menu-content"}`}>
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
                        <button className="menu-item-plateforme" onClick={() => { handleMenuClick('my-offers') }}>{t('plateforme.header.myoffers')}</button>
                        <button className="account-button-plateforme" onClick={() => { handleMenuClick('account-settings') }}>{t('plateforme.header.myprofile')}</button>
                    </div>
                </div>
            </header>
        </div>
    );
}

export default HeaderPlateforme;
