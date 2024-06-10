import React from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faGavel, faHeartbeat, faMagnifyingGlassChart } from '@fortawesome/free-solid-svg-icons';
import '../../css/InfoBand.css'; 

const InfoBand = () => {
    return (
        
        <section className="background-section">
            <div className='info-band'>
                <h2>A qui s'adresse notre solution:</h2>
                <div className="info-items">
                    <div className="info-item">
                    <FontAwesomeIcon icon={faHeartbeat} className="icon" />
                    <div>
                        <h3>1. Les passionnés</h3>
                        <p>Particuliers curieux du monde de l'art, ayant des oeuvres à estimer en vue d'une acquisition prochaine ou d'une vente future potentielle.</p>
                    </div>
                    </div>
                    <div className="info-item">
                    <FontAwesomeIcon icon={faMagnifyingGlassChart} className="icon" />
                    <div>
                        <h3>2. Les experts de l'art</h3>
                        <p>Expert ou assureur voulant évaluer des oeuvres d'art, donner des points de référence à ses clients ou tout simplement valider ses estimations.</p>
                    </div>
                    </div>
                    <div className="info-item">
                    <FontAwesomeIcon icon={faGavel} className="icon" />
                    <div>
                        <h3>3. Les commissaires priseurs</h3>
                        <p>Commissaire priseur organisant des ventes aux enchères quelque soit le domaine d'objet d'art, voulant valider les esimations de sa vente et l'organiser au mieux. </p>
                    </div>
                    </div>
                </div>
            </div>
        </section>
    );
}

export default InfoBand;