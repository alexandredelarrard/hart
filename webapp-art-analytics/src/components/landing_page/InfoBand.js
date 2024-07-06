import React from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faGavel, faHeartbeat, faMagnifyingGlassChart } from '@fortawesome/free-solid-svg-icons';
import '../../css/InfoBand.css';

const InfoBand = ({t}) => {
    return (

        <section className="background-section">
            <div className='info-band'>
                <h2>{t("landing_page.infoband.title")}</h2>
                <div className="info-items">
                    <div className="info-item">
                    <FontAwesomeIcon icon={faHeartbeat} className="icon" />
                    <div>
                        <h3>{t("landing_page.infoband.passionates")}</h3>
                        <p>{t("landing_page.infoband.passionatedesc")}</p>
                    </div>
                    </div>
                    <div className="info-item">
                    <FontAwesomeIcon icon={faMagnifyingGlassChart} className="icon" />
                    <div>
                        <h3>{t("landing_page.infoband.experts")}</h3>
                        <p>{t("landing_page.infoband.expertdesc")}</p>
                    </div>
                    </div>
                    <div className="info-item">
                    <FontAwesomeIcon icon={faGavel} className="icon" />
                    <div>
                        <h3>{t("landing_page.infoband.commissaires")}</h3>
                        <p>{t("landing_page.infoband.commissairedesc")}</p>
                    </div>
                    </div>
                </div>
            </div>
        </section>
    );
}

export default InfoBand;
