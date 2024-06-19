import React from "react";
import { COMPANY_NAME } from "../../utils/constants";
import { Link } from 'react-router-dom';
import logo_blanc from '../../assets/logo_fond_blanc.jpg';
import '../../css/Header.css';

const HeaderWhite = ({t}) => {

    return (
      <div className="firm-presentation">
        <header className="navbar-scrolled">
            <div className="logo-container">
                <a href="/" className="logo">
                    <img src={logo_blanc} alt="Firm Logo" className="firm-logo"/>
                </a>
                <span className="company-name">{COMPANY_NAME}</span>
            </div>
            <Link to="/login">
              <button className="account-button">{t("landing_page.header.myaccount")}</button>
            </Link>
        </header>
    </div>);
}
export default HeaderWhite;