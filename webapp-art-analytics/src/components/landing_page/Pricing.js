import React from "react";
import "../../css/Pricing.css";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUser, faBuilding, faShieldAlt, faCheck, faTimes } from '@fortawesome/free-solid-svg-icons';

const Pricing = () => {
    return (
        <div>
            <section className="pricing-section" id="pricing">
                <div className="pricing-subsection">
                    <h1>Des offres dédiées à vos besoins</h1>
                    <div className="pricing-cards">
                        <div className="pricing-card">
                            <FontAwesomeIcon icon={faUser} className="pricing-icon" />
                            <h2>Individual art lover</h2>
                            <p>Ideal for individual art lovers who want to track and analyze art market trends.</p>
                            <ul className="features-list">
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" /> 10 requests/month</li>
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" /> 5 price estimates/month</li>
                                <li><FontAwesomeIcon icon={faTimes} className="red-icon" /> Auction optimizer</li>
                                <li><FontAwesomeIcon icon={faTimes} className="red-icon" /> Signature authentication</li>
                            </ul>
                            <form className="pricing-form">
                                <div className="price-option">
                                    <FontAwesomeIcon icon={faUser} className="price-icon" />
                                    <label>
                                        <input type="radio" name="individual-price" value="monthly" />
                                        Monthly Price: 10 euros
                                    </label>
                                </div>
                                <div className="price-option">
                                    <FontAwesomeIcon icon={faUser} className="price-icon" />
                                    <label>
                                        <input type="radio" name="individual-price" value="yearly" />
                                        Yearly Subscription: 100 euros
                                    </label>
                                </div>
                            </form>
                            <div className="button-container">
                                <button className="cta-button" onClick={() => window.location.href='/payment'}>Get started</button>
                            </div>
                        </div>
                        <div className="pricing-card">
                            <FontAwesomeIcon icon={faBuilding} className="pricing-icon" />
                            <h2>Business art expert</h2>
                            <p>Perfect for art businesses looking for deep market insights and trends.</p>
                            <ul className="features-list">
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" /> 100 requests/month</li>
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" /> 50 price estimates/month</li>
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" /> Auction optimizer</li>
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" /> Signature authentication</li>
                            </ul>
                            <form className="pricing-form">
                                <div className="price-option">
                                    <FontAwesomeIcon icon={faBuilding} className="price-icon" />
                                    <label>
                                        <input type="radio" name="business-price" value="monthly" />
                                        Monthly Price: 50 euros
                                    </label>
                                </div>
                                <div className="price-option">
                                    <FontAwesomeIcon icon={faBuilding} className="price-icon" />
                                    <label>
                                        <input type="radio" name="business-price" value="yearly" />
                                        Yearly Subscription: 500 euros
                                    </label>
                                </div>
                            </form>
                            <div className="button-container">
                                <button className="cta-button" onClick={() => window.location.href='/payment'}>Get started</button>
                            </div>
                        </div>
                        <div className="pricing-card">
                            <FontAwesomeIcon icon={faShieldAlt} className="pricing-icon" />
                            <h2>Insurers</h2>
                            <p>Best for insurers who need comprehensive art market data and risk assessment.</p>
                            <ul className="features-list">
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" /> 200 requests/month</li>
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" /> 100 price estimates/month</li>
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" /> Auction optimizer</li>
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" /> Signature authentication</li>
                            </ul>
                            <div className="button-container">
                                <button className="cta-button" onClick={() => window.location.href='/contact'}>Contact us</button>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}

export default Pricing;

