import React from 'react';
import HeaderPlateforme from "./utils/HeaderPlateforme.js";

function SearchArt({handleMenuClick, t}) {

  return (
    <div className="upload-form-container">
      <HeaderPlateforme 
        handleMenuClick={handleMenuClick}
      />
      <h2>{t("plateforme.searchart.searchtitle")}</h2>
      <p>{t("plateforme.searchart.searchdesc")}</p>
    </div>
  );
}

export default SearchArt;