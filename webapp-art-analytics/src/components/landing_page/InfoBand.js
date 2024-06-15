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
                        <p>Particuliers curieux du monde de l'art, ayant des oeuvres à estimer, dans le cadre d'une acquisition ou d'un héritage.</p>
                    </div>
                    </div>
                    <div className="info-item">
                    <FontAwesomeIcon icon={faMagnifyingGlassChart} className="icon" />
                    <div>
                        <h3>2. Les experts de l'art</h3>
                        <p>Expert voulant évaluer une oeuvre d'art, partager les références à ses clients ou tout simplement contre expertiser son estimation en quelques secondes.</p>
                    </div>
                    </div>
                    <div className="info-item">
                    <FontAwesomeIcon icon={faGavel} className="icon" />
                    <div>
                        <h3>3. Les commissaires priseurs</h3>
                        <p>Commissaire priseur organisant des ventes aux enchères pour tout objet d'art, voulant valider les esimations de sa vente puis l'organiser au mieux. </p>
                    </div>
                    </div>
                </div>
            </div>
        </section>
    );
}

export default InfoBand;