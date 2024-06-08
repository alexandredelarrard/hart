import React from "react";
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowRight } from '@fortawesome/free-solid-svg-icons';
import { COMPANY_NAME } from "../../utils/constants";
import illustration from '../../assets/landing_background.jpg';

import '../../css/FirmPresentation.css';

const FirmPresentation = () => {

    return (
      <div className="firm-presentation">
        <main className="main-content"> 
          <div className="content">
            <h1><div className="blue">Première plateforme</div> d'intelligence artificielle au service de l'art.</h1>
            <p>
              {COMPANY_NAME} met l'IA au service des professionnels de l'art. 
              Expertisez avec précision, ajustez votre estimation, gagnez en créativité !
            </p>
            <div className="contentainer-firm-presentation-button">
              <Link to="/trial">
                <button className="firm-presentation-cta-button">Essayez gratuitement <span className="button-arrow"><FontAwesomeIcon icon={faArrowRight}/></span></button>
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
