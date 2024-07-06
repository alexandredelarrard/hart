import React from "react";
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowRight } from '@fortawesome/free-solid-svg-icons';
import { COMPANY_NAME } from "../../utils/constants";
import illustration from '../../assets/landing_background.jpg';

import '../../css/FirmPresentation.css';

const FirmPresentation = ({t}) => {

    return (
      <div className="firm-presentation">
        <main className="main-content">
          <div className="content">
            <h1><div className="blue">{t("landing_page.firmpresentation.bluesupertitle")}</div> {t("landing_page.firmpresentation.supertitle")}</h1>
            <p>
              {COMPANY_NAME} {t("landing_page.firmpresentation.supertitledesc")}
            </p>
            <div className="contentainer-firm-presentation-button">
              <Link to="/trial">
                <button className="firm-presentation-cta-button">{t("overall.starttrial")}<span className="button-arrow"><FontAwesomeIcon icon={faArrowRight}/></span></button>
              </Link>
            </div>
          </div>
          <div className="illustration">
            <img src={illustration} alt="Illustration"/>
          </div>
        </main>
      </div>
    );
  };

export default FirmPresentation;
