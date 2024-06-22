import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ROOT_PICTURE } from '../../../utils/constants';
import Carousel from 'react-bootstrap/Carousel';

import 'bootstrap/dist/css/bootstrap.min.css';
import '../../../css/CardDetail.css';


function CardDetail({t}) {
  const navigate = useNavigate();
  const location = useLocation();
  const item = location.state?.item; // Use optional chaining to safely access item

  if (!item) {
    return <div>Item not found</div>;
  }

  return (
    <div className="card-detail-container">
      <button className="back-button" onClick={() => navigate(-1)}>Back</button>
      <div className="card-detail">
        <div className="card-detail-images">
        <Carousel>
            {item.pictures.map((pictureId, index) => (
              <Carousel.Item key={index}>
                <div className="card-detail-image">
                  <img
                    src={`${ROOT_PICTURE}/${item.seller}/pictures/${pictureId}.jpg`}
                    alt={item.title}
                  />
                </div>
              </Carousel.Item>
            ))}
          </Carousel>
        </div>
        <div className="card-detail-info">
          <h2>{item.title}</h2>
          <p><strong>Description:</strong> {item.description}</p>
          <p><strong>Localisation:</strong> {item.localisation}</p>
          <p><strong>House:</strong> {item.house}</p>
          <p><strong>Date:</strong> {item.date}</p>
          <p><strong>Estimate:</strong> {item.estimate_min} - {item.estimate_max} €</p>
          <p><strong>Final Result:</strong> {item.final_result} €</p>
          {item.url_full_detail && (
            <p><a href={item.url_full_detail} target="_blank" rel="noopener noreferrer" className="card-link-detail">
                <strong>URL:</strong> View Full Details
              </a></p>
            )}
        </div>
      </div>
    </div>
  );
}

export default CardDetail;