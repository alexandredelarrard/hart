import React from "react";
import Header from "./Header.js";
import illustration from '../../assets/landing_background_2.jpg';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faDatabase, faDashboard, faCommentsDollar, faSitemap, faBrain, faChartSimple } from '@fortawesome/free-solid-svg-icons';

import '../../css/About.css';
import { COMPANY_NAME } from "../../utils/constants.js";

const About = ({ changeLanguage, t }) => {
    const replaceCompanyName = (text) => text.replace(/{COMPANY_NAME}/g, COMPANY_NAME);
    return (
        <div>
            <Header changeLanguage={changeLanguage} scrolled={true} t={t} />
            <div className="about-intro">
                <img src={illustration} alt="Illustration" />
                <h1>{replaceCompanyName(t('landing_page.about.h1_title'))}</h1>
            </div>
            <div className="about-container">
                <section className="about-aim">
                    <h2>{t('landing_page.about.h2_title_1')}</h2>
                    <p>{replaceCompanyName(t('landing_page.about.mission_statement_1'))}</p>
                    <div className="quote">{t('landing_page.about.quote')}</div>
                    <p>{t('landing_page.about.mission_statement_2')}</p>
                    <p>{replaceCompanyName(t('landing_page.about.mission_statement_3'))}</p>
                    <ul>
                        <li><FontAwesomeIcon icon={faDashboard} className="icon" />{t('landing_page.about.aim_1')}</li>
                        <li><FontAwesomeIcon icon={faCommentsDollar} className="icon" />{t('landing_page.about.aim_2')}</li>
                        <li><FontAwesomeIcon icon={faSitemap} className="icon" />{t('landing_page.about.aim_3')}</li>
                    </ul>
                </section>
                <section className="about-how">
                    <h2>{t('landing_page.about.h2_title_2')}</h2>
                    <p>{t('landing_page.about.how_1')}</p>
                    <p>{t('landing_page.about.how_2')}</p>
                    <ul>
                        <li><FontAwesomeIcon icon={faDatabase} className="icon" />{t('landing_page.about.tool_1')}</li>
                        <li><FontAwesomeIcon icon={faBrain} className="icon" />{t('landing_page.about.tool_2')}</li>
                        <li><FontAwesomeIcon icon={faChartSimple} className="icon" />{t('landing_page.about.tool_3')}</li>
                    </ul>
                    <p>{t('landing_page.about.how_3')}</p>
                </section>
                <section className="contact-us">
                    <p>{t('landing_page.about.contact_us')}</p>
                    <div className="button-container">
                        <button className="firm-presentation-cta-button" onClick={() => window.location.href='/contact'}>{t("overall.contactus")}</button>
                    </div>
                </section>
            </div>
        </div>
    );
}

export default About;
