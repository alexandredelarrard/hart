import React from 'react';
import HeaderWhite from "./landing_page/Header_white.js";
import '../css/ResetPassword.css';

function Confirm() {
  
  return (
    <div>
      <HeaderWhite/>
        <div className="reset-password-container">
            <h2>Email confirmé</h2>
        </div>
    </div>
  );
}

export default Confirm;