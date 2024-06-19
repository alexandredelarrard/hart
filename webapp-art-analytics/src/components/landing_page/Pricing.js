import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUser, faBuilding, faShieldAlt, faCheck} from '@fortawesome/free-solid-svg-icons';

import "../../css/Pricing.css";
import { COMPANY_NAME } from '../../utils/constants';

const Pricing = ({isplateforme, activePlan, remainingDays, closestQueries, t}) => {
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
            <section className={isplateforme? "pricing-section-plateforme": "pricing-section"}>
                <div className={isplateforme? "pricing-subsection-plateforme" : "pricing-subsection"} id="pricing">
                    <h1>{t("landing_page.pricing.pricingtitle")}</h1>
                    <div className="pricing-cards">
                        <div className={activePlan === "free_plan" ? "pricing-card prefered" : "pricing-card"}>
                            <FontAwesomeIcon icon={faBuilding} className="pricing-icon" />
                            <h2>{t("landing_page.pricing.newoffertitle")}</h2>
                            <p>{t("landing_page.pricing.newofferdesc")}{COMPANY_NAME}.</p>
                            <ul className="features-list">
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" />{t("landing_page.pricing.newcriterion1")}</li>
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" />{t("landing_page.pricing.newcriterion2")}</li>
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" />{t("landing_page.pricing.newcriterion3")}</li>
                            </ul>
                            {isplateforme && (
                                <>
                                   <ul>
                                        <li className='sub-li-plan'> {t("landing_page.pricing.remainingdays")}: {remainingDays}</li>
                                        <li className='sub-li-plan'> {t("landing_page.pricing.remainingclosequeries")}: {closestQueries}</li>
                                    </ul>
                                </>
                                )}
                            <div className="button-container">
                                <button
                                    className="firm-presentation-cta-button"
                                    onClick={() => handleSubmit('beginner')}
                                    disabled={activePlan === "free_plan"}
                                >
                                    {activePlan === "free_plan" ? t("overall.currentplan") : t("overall.startnow")}
                                </button>
                            </div>
                        </div>
                        <div className={activePlan === "individual_plan" ? "pricing-card prefered" : "pricing-card"}>
                            <FontAwesomeIcon icon={faUser} className="pricing-icon" />
                            <h2>{t("landing_page.pricing.passionatetitle")}</h2>
                            <p>{t("landing_page.pricing.passionatedesc")}</p>
                            <ul className="features-list">
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" />{t("landing_page.pricing.passionatecriterion1")}</li>
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" />{t("landing_page.pricing.passionatecriterion2")}</li>
                            </ul>
                            <div className="price-options">
                                <div className="price-column">
                                    <h3>{t("overall.monthly")}</h3>
                                    <div 
                                        className={`price-option ${selectedPrice['individual'] === 'monthly' ? 'selected' : ''}`}
                                        onClick={() => handlePriceSelection('individual', 'monthly')}
                                    >
                                        <span className="price-amount">{t("landing_page.pricing.monthlypricepassion")} {t("overall.currency")}</span>
                                    </div>
                                </div>
                                <div className="price-column">
                                    <h3>{t("overall.yearly")}</h3>
                                    <div 
                                        className={`price-option ${selectedPrice['individual'] === 'yearly' ? 'selected' : ''}`}
                                        onClick={() => handlePriceSelection('individual', 'yearly')}
                                    >
                                        <span className="price-amount">{t("landing_page.pricing.yearlypricepassion")} {t("overall.currency")}</span>
                                    </div>
                                </div>
                            </div>
                            <div className="button-container">
                                <button
                                    className="firm-presentation-cta-button"
                                    onClick={() => handleSubmit('individual')}
                                >
                                    {t("overall.enroll")}
                                </button>
                            </div>
                        </div>
                        <div className={activePlan === "custome_plan" ? "pricing-card prefered" : "pricing-card"}>
                            <FontAwesomeIcon icon={faShieldAlt} className="pricing-icon" />
                            <h2>{t("landing_page.pricing.experttitle")}</h2>
                            <p>{t("landing_page.pricing.expertdesc")}</p>
                            <ul className="features-list">
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" />{t("landing_page.pricing.expertcriterion1")}</li>
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" />{t("landing_page.pricing.expertcriterion2")}</li>
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" />{t("landing_page.pricing.expertcriterion3")}</li>
                                <li><FontAwesomeIcon icon={faCheck} className="green-icon" />{t("landing_page.pricing.expertcriterion4")}</li>
                            </ul>
                            <div className="button-container">
                                <button className="firm-presentation-cta-button" onClick={() => window.location.href='/contact'}>{t("overall.contactus")}</button>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}

export default Pricing;

