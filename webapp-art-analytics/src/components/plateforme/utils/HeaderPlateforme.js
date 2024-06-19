import React from "react";
import { COMPANY_NAME } from "../../../utils/constants";
import { useTranslation } from 'react-i18next';
import logo_blanc from '../../../assets/logo_fond_blanc.jpg';
import '../../../css/HeaderPlateforme.css';


const HeaderPlateforme = ({handleMenuClick}) => {

    const { i18n } = useTranslation();

    const changeLanguage = (lng) => {
        i18n.changeLanguage(lng);
    };
    const { t } = useTranslation();

    return (
      <div className="firm-presentation-plateforme">
        <header className="navbar-scrolled-plateforme">
            <div className="logo-container-plateforme">
                <a href="/" className="logo-plateforme">
                    <img src={logo_blanc} alt="Firm Logo" className="firm-logo"/>
                </a>
                <span className="company-name-plateforme">{COMPANY_NAME}</span>
            </div>
            <div className="menu-container-plateforme">
                <button className="menu-item-plateforme" onClick={() => changeLanguage('en')}>English</button>
                <button className="menu-item-plateforme" onClick={() => changeLanguage('fr')}>Français</button>
                <button className="menu-item-plateforme" onClick={() => { handleMenuClick('my-offers')}}>{t('plateforme.header.myoffers')}</button>
                <button className="account-button-plateforme" onClick={() => { handleMenuClick('account-settings')}}>{t('plateforme.header.myprofile')}</button>
            </div>
        </header>
    </div>);
}
export default HeaderPlateforme;