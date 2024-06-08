import React from "react";
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCopyright, faEnvelope } from '@fortawesome/free-solid-svg-icons';
import { faLinkedin, faInstagram, faTwitter } from '@fortawesome/free-brands-svg-icons';
import logo from '../../assets/logo_fond_blanc.jpg';  // Placeholder for your company logo
import '../../css/Footer.css';

const Footer = () => {
    return (
        <footer className="footer-section">
            <hr className="footer-separator" />
            <div className="footer-container">
                <div className="footer-column">
                    <form className="newsletter-form">
                        <h4>Newsletter</h4>
                        <input type="email" placeholder="Your email address" />
                        <button type="submit">
                            <FontAwesomeIcon icon={faEnvelope} />
                        </button>
                    </form>
                </div>
                <div className="footer-column">
                    <div className="footer-company-info">
                        <FontAwesomeIcon icon={faCopyright} />  
                        {/* <img src={logo} alt="Company Logo" className="footer-logo" /> */}
                        <div>
                            <span>   Artycs 2024</span>
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
                    <h3>Product</h3>
                    <Link to="/product1">Product 1</Link>
                    <Link to="/product2">Product 2</Link>
                    <Link to="/product3">Product 3</Link>
                    <Link to="/product4">Product 4</Link>
                    <Link to="/pricing">Pricing</Link>
                    <Link to="/legal">Legal</Link>
                </div>
                <div className="footer-column">
                    <h3>Artycs</h3>
                    <Link to="/about">About</Link>
                    <Link to="/contact">Contact Us</Link>
                    <Link to="/team">Team</Link>
                    <Link to="/career">Career</Link>
                </div>
                <div className="footer-column">
                    <h3>Community</h3>
                    <Link to="/reviews">Reviews</Link>
                    <Link to="/blog">Blog</Link>
                    <Link to="/external-links">External Links</Link>
                </div>
            </div>
        </footer>
    );
}

export default Footer;