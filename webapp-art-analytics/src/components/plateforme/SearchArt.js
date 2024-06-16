import React from 'react';
import HeaderPlateforme from "../landing_page/HeaderPlateforme.js";

function SearchArt({handleMenuClick}) {
  return (
    <div className="upload-form-container">
      <HeaderPlateforme 
        handleMenuClick={handleMenuClick}
      />
      <h2>Search your art piece</h2>
      <p>This is the search element</p>
    </div>
  );
}

export default SearchArt;