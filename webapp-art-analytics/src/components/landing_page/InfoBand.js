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
                        <p>Estimez en toute autonomie vos propres biens à partir d'une simple photo ou d'un descriptif</p>
                    </div>
                    </div>
                    <div className="info-item">
                    <FontAwesomeIcon icon={faMagnifyingGlassChart} className="icon" />
                    <div>
                        <h3>2. Les experts de l'art</h3>
                        <p>Comparez vos biens aux ventes passées en quelques secondes. Affinez vos recherche à partir de nos multiples critères</p>
                    </div>
                    </div>
                    <div className="info-item">
                    <FontAwesomeIcon icon={faGavel} className="icon" />
                    <div>
                        <h3>3. Les commissaires priseurs</h3>
                        <p>Optimisez la répartition de vos lots afin de maximiser vos chances de ventes. Estimez les chances de succés de vente d'un lot. </p>
                    </div>
                    </div>
                </div>
            </div>
        </section>
    );
}

export default InfoBand;