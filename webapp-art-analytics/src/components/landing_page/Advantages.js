import React from "react";

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBusinessTime, faHandshake, faSitemap, faGlobe } from '@fortawesome/free-solid-svg-icons';

import "../../css/Advantages.css";

const Advantages = ({ t }) => {

    const advantagesData = [
        {
            image: faGlobe,
            title: t("landing_page.advantages.title_1"),
            description: [
                t("landing_page.advantages.desc_1_1"),
                t("landing_page.advantages.desc_1_2"),
                t("landing_page.advantages.desc_1_3")
            ]
        },
        {
            image: faHandshake,
            title: t("landing_page.advantages.title_2"),
            description: [
                t("landing_page.advantages.desc_2_1"),
                t("landing_page.advantages.desc_2_2"),
                t("landing_page.advantages.desc_2_3")
            ]
        },
        {
            image: faSitemap,
            title: t("landing_page.advantages.title_3"),
            description: [
                t("landing_page.advantages.desc_3_1"),
                t("landing_page.advantages.desc_3_2"),
                t("landing_page.advantages.desc_3_3")
            ]
        },
        {
            image: faBusinessTime,
            title: t("landing_page.advantages.title_4"),
            description: [
                t("landing_page.advantages.desc_4_1"),
                t("landing_page.advantages.desc_4_2"),
                t("landing_page.advantages.desc_4_3")
            ]
        },
    ];

    return (
        <div className="advantages-background-container">
            <div className="advantages-container">
                <h2>{t("landing_page.advantages.title")}</h2>
                <div className="advantage-cards">
                    {advantagesData.map((advantage, index) => (
                        <div className="advantage-card" key={index}>
                            <div className="advantage-icon">
                                <FontAwesomeIcon icon={advantage.image}  size="2x"/>
                            </div>
                            <div className="advantage-content">
                                <h3>{advantage.title}</h3>
                                <ul>
                                    {advantage.description.map((desc, i) => (
                                        <li key={i}>{desc}</li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default Advantages;
