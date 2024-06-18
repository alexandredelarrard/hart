import React, { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUser, faBuilding, faShieldAlt, faCheck} from '@fortawesome/free-solid-svg-icons';

import "../../css/Pricing.css";
import { COMPANY_NAME } from '../../utils/constants';

const Pricing = ({isplateforme, activePlan, remainingDays, closestQueries}) => {
    const [selectedPrice, setSelectedPrice] = useState({});

    const handlePriceSelection = (category, priceType) => {
        setSelectedPrice({ ...selectedPrice, [category]: priceType });
    };

    const handleSubmit = (category) => {
        console.log(`Selected price for ${category}:`, selectedPrice[category]);
        // Add logic for form submission, e.g., redirect to payment with selected price
        if(category === 'beginner'){
            window.location.href = '/trial';
        }
        else{
            window.location.href = '/enroll';
        }
    };

    return (
        <div>
            <section className={isplateforme? "pricing-section-plateforme": "pricing-section"} id="pricing">
                <div className={isplateforme? "pricing-subsection-plateforme" : "pricing-subsection"}>
                    <h1>Des offres dédiées à vos besoins</h1>
                    <div className="pricing-cards">
                        <div className={activePlan === "free_plan" ? "pricing-card prefered" : "pricing-card"}>
                            <FontAwesomeIcon icon={faBuilding} className="pricing-icon" />
                            <h2>Les nouveaux</h2>
                            <p>Essai gratuit pendant 7 jours pour vous familiariser avec les fonctionnalités d'{COMPANY_NAME}.</p>
                            <ul className="features-list">
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" /> Jusqu'à 100 recherches</li>
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" /> 40 estimations </li>
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" /> Valable 7 jours </li>
                            </ul>
                            {isplateforme && (
                                <>
                                   <ul>
                                        <li className='sub-li-plan'> Jours restants: {remainingDays}</li>
                                        <li className='sub-li-plan'> Requêtes restantes : {closestQueries}</li>
                                    </ul>
                                </>
                                )}
                            <div className="button-container">
                                <button
                                    className="firm-presentation-cta-button"
                                    onClick={() => handleSubmit('beginner')}
                                    disabled={activePlan === "free_plan"}
                                >
                                    {activePlan === "free_plan" ? "Mon plan actuel": "Essayer gratuitement"}
                                </button>
                            </div>
                        </div>
                        <div className={activePlan === "individual_plan" ? "pricing-card prefered" : "pricing-card"}>
                            <FontAwesomeIcon icon={faUser} className="pricing-icon" />
                            <h2>Passionnés d'art</h2>
                            <p>Idéal pour les passionnés d'art, curieux d'un artiste ou de la valeur d'une oeuvre</p>
                            <ul className="features-list">
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" /> Recherches illimitées </li>
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" /> 200 estimations/mois </li>
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
                        <div className={activePlan === "custome_plan" ? "pricing-card prefered" : "pricing-card"}>
                            <FontAwesomeIcon icon={faShieldAlt} className="pricing-icon" />
                            <h2>Entreprises/Experts</h2>
                            <p>Entreprises ou experts ayant des besoins importants requérant une offre à la carte.</p>
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

