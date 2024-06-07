import React from "react";
import { Link } from 'react-router-dom';
import { COMPANY_NAME } from "../../utils/constants";
import illustration from '../../assets/landing_background.jpg';

import '../../css/FirmPresentation.css';

const FirmPresentation = () => {

    return (
      <div className="firm-presentation">
        <main className="main-content"> 
          <div className="content">
            <h1>Première plateforme d'intelligence artificielle au service de l'art.</h1>
            <p>
              {COMPANY_NAME} met l'intelligence artificielle au service des professionnels de l'art. 
              Expertisez avec précision, ajustez votre estimation, gagnez en créativité !
            </p>
            <Link to="/login">
              <button className="cta-button">Let's Build It!</button>
            </Link>
          </div>
          <div className="illustration">
            <img src={illustration} alt="Illustration"/>
          </div>
        </main>
      </div>
    );
  };
  
export default FirmPresentation;
