import React from 'react';
import HeaderPlateforme from "./utils/HeaderPlateforme.js";

function OptimizeSale({handleMenuClick, t}) {

  return (
    <div className="upload-form-container">
      <HeaderPlateforme 
        handleMenuClick={handleMenuClick}
      />
      <h2>{t("plateforme.optimize.optimizetitle")}</h2>
      <p>{t("plateforme.optimize.optimizedesc")}</p>
    </div>
  );
}

export default OptimizeSale;