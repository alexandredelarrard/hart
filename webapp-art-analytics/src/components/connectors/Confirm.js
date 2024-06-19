import React from 'react';
import HeaderWhite from "../landing_page/Header_white.js";
import '../../css/ResetPassword.css';

function Confirm({t}) {
  
  return (
    <div>
      <HeaderWhite t={t}/>
        <div className="reset-password-container">
            <h2>{t("landing_page.confirmemail.title")}</h2>
        </div>
    </div>
  );
}

export default Confirm;