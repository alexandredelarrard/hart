import React from 'react';
import Header from "../landing_page/Header.js";

function ComingSoon({t, changeLanguage}) {

  return (
    <div>
      <Header changeLanguage={changeLanguage} scrolled={true} t={t}/>
      <div className="login-container">
      <div className="login-form">
        <h2>
            {t('overall.coming_soon')}
        </h2>
        <div className='quote'>
          {t('overall.building_process')}
        </div>
      </div>
    </div>
    </div>
  );
}

export default ComingSoon;
