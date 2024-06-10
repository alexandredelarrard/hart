import React from "react";
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCopyright, faEnvelope } from '@fortawesome/free-solid-svg-icons';
import { faLinkedin, faInstagram, faTwitter } from '@fortawesome/free-brands-svg-icons';
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
                    <a href="#product_1">Search</a>
                    <a href="#product_2">Estimate</a>
                    <a href="#product_3">Optimize sale</a>
                    <a href="#product_4">Authenticate art piece</a>
                    <a href="#pricing">Pricing</a>
                    <Link to="/legal">Legal</Link>
                </div>
                <div className="footer-column">
                    <h3>Artycs</h3>
                    <Link to="/about">About Artycs</Link>
                    <Link to="/contact">Contact Us</Link>
                    <Link to="/team">Team</Link>
                    {/* <Link to="/career">Career</Link> */}
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