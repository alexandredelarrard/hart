import React from 'react';
import '../css/Card.css';
import {ROOT_PICTURE} from '../utils/constants';
import { useNavigate } from 'react-router-dom';

function Card({ item }) {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/card/${item.id_unique}`, { state: { item } });
  };
  
  return (
      <div className="card">
        <div onClick={handleClick} className="card-link">
          <img src={`${ROOT_PICTURE}/${item.seller}/pictures/${item.id_picture}.jpg`} alt={item.title} className="card-image" />
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
              <span className="card-price"><strong>Estimate:</strong> {item.estimate_min} - {item.estimate_max} €</span>
              <span className="card-result"><strong>Final:</strong> {item.final_result} €</span>
            </div>
          </div>
    </div>
  );
}

export default Card;