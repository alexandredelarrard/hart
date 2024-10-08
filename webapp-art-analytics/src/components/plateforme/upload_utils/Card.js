import React from 'react';
import { ROOT_PICTURE, PATHS} from '../../../utils/constants';
import { useNavigate } from 'react-router-dom';
import { formatPrice } from '../../../utils/general.js';
import '../../../css/Card.css';

function Card({ i18n, item, t }) {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`${PATHS["CARD_ID_ROOT"]}${item.id_item}`, { state: { item } });
  };

  const renderImage = () => {
    if (item.id_picture === "NO_PICTURE" || item.id_picture === "FAKE_PICTURE") {
      return (
        <div className="card-placeholder">
          {t("overall.no_picture")}
        </div>
      );
    } else {
      return (
        <img
          src={`${ROOT_PICTURE}/${item.seller}/pictures/${item.id_picture}.jpg`}
          alt={item.title}
          className="card-image"
        />
      );
    }
  };

  return (
    <div className="card">
      <div onClick={handleClick} className="card-link">
        {renderImage()}
        <div className="card-info">
          <span className="card-house">{item.house}</span>
          <span className="card-localisation">{item.localisation}</span>
          <span className="card-date">{item.date}</span>
        </div>
      </div>
      <div className="card-content">
        <h3 className="card-title">{item.title}</h3>
        <p className="card-description">{item.description}</p>
        <div className="card-footer">
          <span className="card-price">
            <strong>{t("plateforme.uploadform.estimationprice")}:</strong>
            {formatPrice(item.estimate_min, i18n.language, false)} - {formatPrice(item.estimate_max, i18n.language, true)}
          </span>
          <span className="card-result">
            <strong>{t("plateforme.uploadform.finalprice")}:</strong>
            {formatPrice(item.final_result, i18n.language, true)}
          </span>
        </div>
      </div>
    </div>
  );
}

export default Card;
