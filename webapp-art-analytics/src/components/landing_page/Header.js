import React, { useEffect, useState } from "react";
import { COMPANY_NAME } from "../../utils/constants";
import { Link } from 'react-router-dom';
import logo from '../../assets/logo.jpg';
import '../../css/Header.css';

const Header = () => {
    const [scrolled, setScrolled] = useState(false);

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
                    <img src={logo} alt="Firm Logo" className="firm-logo"/>
                </a>
                <span className={`company-name ${scrolled ? "company-name-scrolled" : ""}`}>{COMPANY_NAME}</span>
            </div>
            <nav className="nav-links">
                <a href="#product">Product</a>
                <a href="#pricing">Pricing</a>
                <a href="#blog">Blog</a>
            </nav>
            <Link to="/login">
              <button className="account-button">My account</button>
            </Link>
        </header>
    </div>);
}
export default Header;