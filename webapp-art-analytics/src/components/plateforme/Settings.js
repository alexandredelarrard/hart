import React, {useState} from 'react';
import useLogActivity from '../../hooks/general/useLogActivity.js';
import HeaderPlateforme from "./upload_utils/HeaderPlateforme.js";

import ProfileSettings from './general/ProfileSettings.js';
import BillingSettings from './general/BillingSettings.js';

import '../../css/ProfileSettings.css';

function Settings({
  userData,
  setUserData,
  handleMenuClick, 
  changeLanguage,
  t
}) {
  const [activeTab, setActiveTab] = useState('profile');
  const LogActivity = useLogActivity();

  return (
    <div className="upload-form-container">
      <HeaderPlateforme
        changeLanguage={changeLanguage}
        handleMenuClick={handleMenuClick}
        t={t}
      />
      <div className="menu-bar">
        <button className={activeTab === 'profile' ? 'active' : ''} onClick={() => {setActiveTab('profile'); LogActivity("click_profile_menu", "")}}>{t("plateforme.profilesettings.profilebutton")}</button>
        <button className={activeTab === 'billing' ? 'active' : ''} onClick={() => {setActiveTab('billing'); LogActivity("click_billing_menu", "")}}>{t("plateforme.profilesettings.billingbutton")}</button>
      </div>
        {activeTab === 'profile' && (
          <ProfileSettings 
            userData={userData}
            setUserData={setUserData}
            t={t}
        />
        )}
        {activeTab === 'billing' && (
          <BillingSettings 
            t={t}
          />
        )}
    </div>
  );
}
export default Settings;
