import React, { useState, useEffect } from 'react';
import Cookies from 'js-cookie';
import HeaderPlateforme from "../landing_page/HeaderPlateforme.js";
import Pricing from '../landing_page/Pricing.js';

import '../../css/ProfileSettings.css';

function Offers({handleMenuClick}) {
  const [activePlan, setActivePlan] = useState('');

  useEffect(() => {
    const token = Cookies.get('token');
    if (!token) {
      return;
    }

    const userdataCookie = Cookies.get('userdata');
    if (userdataCookie) {
      const parsedUserdata = JSON.parse(userdataCookie);
      setActivePlan(parsedUserdata.activeplan || 'free');
    }
  }, []);
  
  return (
    <div className="upload-form-container">
        <HeaderPlateforme 
            handleMenuClick={handleMenuClick}
        />
        <div className="billing-section">
            <div className="plans">
                <Pricing
                    isplateforme={true}
                />
            </div>
        </div>
    </div>
  );
}

export default Offers;