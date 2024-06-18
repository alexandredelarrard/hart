import React from "react";
import { COMPANY_NAME } from "../../utils/constants";
import logo_blanc from '../../assets/logo_fond_blanc.jpg';
import '../../css/HeaderPlateforme.css';

const HeaderPlateforme = ({handleMenuClick}) => {

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
                <button className="menu-item-plateforme" onClick={() => { handleMenuClick('my-offers')}}>Abonnez-vous</button>
                <button className="account-button-plateforme" onClick={() => { handleMenuClick('account-settings')}}>Mon profile</button>
            </div>
        </header>
    </div>);
}
export default HeaderPlateforme;