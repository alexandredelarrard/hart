import React from 'react';
import HeaderPlateforme from "./upload_utils/HeaderPlateforme.js";

function OptimizeSale({changeLanguage, handleMenuClick, t}) {

  return (
    <div className="upload-form-container">
      <HeaderPlateforme
        changeLanguage={changeLanguage}
        handleMenuClick={handleMenuClick}
        t={t}
      />
      <h2>{t("plateforme.optimize.optimizetitle")}</h2>
      <p>{t("plateforme.optimize.optimizedesc")}</p>
    </div>
  );
}

export default OptimizeSale;
