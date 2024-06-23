import React, { useState, useEffect } from 'react';
import Cookies from 'js-cookie';
import HeaderPlateforme from "./upload_utils/HeaderPlateforme.js";
import Pricing from '../landing_page/Pricing.js';

import '../../css/ProfileSettings.css';

function Offers({changeLanguage, handleMenuClick, t}) {
  const [activePlan, setActivePlan] = useState('individual_plan');
  const [closestQueries, setclosestQueries] = useState('');
  const [remainingDays, setremainingDays] = useState('');

  useEffect(() => {
    const token = Cookies.get('token');
    if (!token) {
      return;
    }
    
    const plan_name = Cookies.get('plan_name');
    const plan_end_date=  Cookies.get('plan_end_date');
    const vol_cosest=  Cookies.get('remaining_closest_volume');
    if (plan_name) {
      setActivePlan(plan_name);
    }
    if (vol_cosest) {
      setclosestQueries(vol_cosest);
    }
    if (plan_end_date) {
      const planEndDate = new Date(plan_end_date);
      const currentDate = new Date();

      // Calculate the difference in time
      const timeDifference = planEndDate - currentDate + 10;
      
      // Convert time difference from milliseconds to days
      const remainingDays = Math.ceil(timeDifference / (1000 * 3600 * 24));
      
      setremainingDays(remainingDays);
    }

  }, [setActivePlan, setclosestQueries]);
  
  return (
    <div className="upload-form-container">
        <HeaderPlateforme 
        changeLanguage={changeLanguage}
        handleMenuClick={handleMenuClick}
        t={t}
      />
        <div className="billing-section">
            <div className="plans">
                <Pricing
                    isplateforme={true}
                    activePlan={activePlan}
                    remainingDays={remainingDays}
                    closestQueries={closestQueries}
                    t={t}
                />
            </div>
        </div>
    </div>
  );
}

export default Offers;