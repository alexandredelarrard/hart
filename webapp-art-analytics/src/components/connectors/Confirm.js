import React from 'react';
import Header from "../landing_page/Header.js";

function Confirm({changeLanguage, t}) {

  return (
    <div>
       <Header changeLanguage={changeLanguage} scrolled={true} t={t}/>
       <div className="login-container">
          <div className="login-form">
              <h2>{t("landing_page.confirmemail.title")}</h2>
          </div>
        </div>
    </div>
  );
}

export default Confirm;
