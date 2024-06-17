import React from 'react';
import PropTypes from 'prop-types';
import '../../../css/ExpertCard.css'; // Assuming you have a CSS file for styling

const ExpertCard = ({ expert }) => {
  return (
    <div className="expert-card">
      <h3>{expert.expert_surname} {expert.expert_surname}</h3>
      <p>Gender: {expert.expert_gender}</p>
      <p>City: {expert.expert_city}</p>
      {/* <p>Distance: {expert.distance.toFixed(2)} km</p> */}
    </div>
  );
};

ExpertCard.propTypes = {
  expert: PropTypes.object.isRequired,
};

export default ExpertCard;