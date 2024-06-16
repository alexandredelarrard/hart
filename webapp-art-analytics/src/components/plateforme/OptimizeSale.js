import React from 'react';
import HeaderPlateforme from "../landing_page/HeaderPlateforme.js";

function OptimizeSale({handleMenuClick}) {
  return (
    <div className="upload-form-container">
      <HeaderPlateforme 
        handleMenuClick={handleMenuClick}
      />
      <h2>Optimize Your Sale</h2>
      <p>This is the Optimize Your Sale component.</p>
    </div>
  );
}

export default OptimizeSale;