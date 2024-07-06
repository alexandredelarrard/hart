import React from 'react';
import PropTypes from 'prop-types';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUserCircle } from '@fortawesome/free-solid-svg-icons';
import { FaPhone, FaEnvelope } from 'react-icons/fa';

import '../../../css/ExpertCard.css'; // Assuming you have a CSS file for styling

const ExpertCard = ({ expert }) => {
  const renderStars = (grade) => {
    const stars = [];
    for (let i = 0; i < 5; i++) {
      stars.push(
        <span key={i} className={i < grade ? 'star filled' : 'star'}>★</span>
      );
    }
    return stars;
  };

  return (
    <div className="expert-card">
      <div className="avatar-container">
        {expert.expert_gender === 'male' ?
          <FontAwesomeIcon icon={faUserCircle} className="avatar" color='#0c3867'/> :
          <FontAwesomeIcon icon={faUserCircle} className="avatar" color='#0c3867'/>
        }
        <span className="expertise">{expert.expert_expertise}</span>
      </div>
      <div className="info-container">
        <div className="row-item">
          <span className="name">{expert.expert_surname} {expert.expert_name}</span>
          <span className="stars">{renderStars(expert.expert_grade)}</span>
        </div>
        <div className="row-item">
          <span className="city">{expert.expert_city}</span>
          <span className="zipcode">{expert.expert_zipcode}</span>
        </div>
        <div className="row-item">
          <span className="phone"><FaPhone color='#0c3867'/> {expert.expert_cellphone}</span>
          <span className="email"><FaEnvelope color='#0c3867'/> {expert.expert_email}</span>
        </div>
      </div>
    </div>
  );
};

ExpertCard.propTypes = {
  expert: PropTypes.shape({
    expert_name: PropTypes.string.isRequired,
    expert_surname: PropTypes.string.isRequired,
    expert_grade: PropTypes.number.isRequired,
    expert_city: PropTypes.string.isRequired,
    expert_zipcode: PropTypes.string.isRequired,
    expert_email: PropTypes.string.isRequired,
    expert_cellphone: PropTypes.string.isRequired,
    expert_gender: PropTypes.string.isRequired,
  }).isRequired,
};

export default ExpertCard;
