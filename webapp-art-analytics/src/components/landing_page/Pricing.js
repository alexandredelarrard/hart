import React, { useState } from 'react';
import "../../css/Pricing.css";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUser, faBuilding, faShieldAlt, faCheck, faTimes } from '@fortawesome/free-solid-svg-icons';

const Pricing = () => {
    const [selectedPrice, setSelectedPrice] = useState({});

    const handlePriceSelection = (category, priceType) => {
        setSelectedPrice({ ...selectedPrice, [category]: priceType });
    };

    const handleSubmit = (category) => {
        console.log(`Selected price for ${category}:`, selectedPrice[category]);
        // Add logic for form submission, e.g., redirect to payment with selected price
        window.location.href = '/enroll';
    };

    return (
        <div>
            <section className="pricing-section" id="pricing">
                <div className="pricing-subsection">
                    <h1>Des offres dédiées à vos besoins</h1>
                    <div className="pricing-cards">
                        <div className="pricing-card">
                            <FontAwesomeIcon icon={faUser} className="pricing-icon" />
                            <h2>Passionnés d'art</h2>
                            <p>Idéal pour les passionnés d'art, curieux d'un artiste ou de la valeur d'une oeuvre d'art</p>
                            <ul className="features-list">
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" /> Recherches illimitées </li>
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" /> 20 estimations/mois </li>
                            </ul>
                            <div className="price-options">
                                <div className="price-column">
                                    <h3>Mensuel</h3>
                                    <div 
                                        className={`price-option ${selectedPrice['individual'] === 'monthly' ? 'selected' : ''}`}
                                        onClick={() => handlePriceSelection('individual', 'monthly')}
                                    >
                                        <span className="price-amount">19 €</span>
                                    </div>
                                </div>
                                <div className="price-column">
                                    <h3>Annuel</h3>
                                    <div 
                                        className={`price-option ${selectedPrice['individual'] === 'yearly' ? 'selected' : ''}`}
                                        onClick={() => handlePriceSelection('individual', 'yearly')}
                                    >
                                        <span className="price-amount">199 €</span>
                                    </div>
                                </div>
                            </div>
                            <div className="button-container">
                                <button
                                    className="firm-presentation-cta-button"
                                    onClick={() => handleSubmit('individual')}
                                >
                                    S'abonner
                                </button>
                            </div>
                        </div>
                        <div className="pricing-card">
                            <FontAwesomeIcon icon={faBuilding} className="pricing-icon" />
                            <h2>Experts</h2>
                            <p>Pour les experts devant évaluer ou authentifier des oeuvres d'art.</p>
                            <ul className="features-list">
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" /> Recherches illimitées </li>
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" /> 200 estimations/mois</li>
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" /> Optimiseur de vente </li>
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" /> Outil d'authentification</li>
                            </ul>
                            <div className="button-container">
                                <button className="firm-presentation-cta-button disabled-button" disabled>
                                    Bientôt disponible
                                </button>
                            </div>
                        </div>
                        <div className="pricing-card">
                            <FontAwesomeIcon icon={faShieldAlt} className="pricing-icon" />
                            <h2>Entreprises</h2>
                            <p>Entreprises ayant des besoins importants requérant une offre à la carte.</p>
                            <ul className="features-list">
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" /> Requêtes sans limite</li>
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" /> Limite d'estimations dédiée</li>
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" /> Support de ventes </li>
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" /> Authentification à la carte</li>
                            </ul>
                            <div className="button-container">
                                <button className="firm-presentation-cta-button" onClick={() => window.location.href='/contact'}>Nous contacter</button>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}

export default Pricing;

