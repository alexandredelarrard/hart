import React from "react";
import { Link } from 'react-router-dom';

const Footer = () => {
    return (
        <footer className="footer">
            <p>&copy; 2024 Art Analytics. All rights reserved.</p>
            <div className="footer-links">
                <Link to="/">Team</Link>
                <Link to="/">Contact</Link>
                <Link to="/">Pricing</Link>
            </div>
        </footer>
        );
}
export default Footer;
