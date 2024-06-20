import React, { useState} from 'react';
import axios from 'axios';
import useLogActivity from '../../hooks/general/useLogActivity.js';
import HeaderPlateforme from "./upload_utils/HeaderPlateforme.js";
import PaymentTable from "../plateforme/upload_utils/PaymentTable.js"
import {URL_API, URL_UPDATE_PROFILE} from "../../utils/constants.js";
import useFetchPayments from '../../hooks/plateforme/useFetchPayments.js';

import '../../css/ProfileSettings.css';

function BillingSettings({payments, t}) {

  return (
    <div className="my-payment-section">
      <h2>{t("plateforme.profilesettings.billingtitle")}</h2>
      <div className="plans">
        <div className="">
            <PaymentTable 
              payments={payments}
            />
        </div>
      </div>
    </div>
  );
}

function ProfileSettings({handleMenuClick, t}) {
  const [userData, setUserData] = useState({});
  const [editMode, setEditMode] = useState(false);
  const [name, setName] = useState('');
  const [surname, setSurname] = useState('');
  const [address, setAddress] = useState('');
  const [emailValidated, setEmailValidated] = useState(false);
  const [validationDate, setValidationDate] = useState(null);
  const [activeTab, setActiveTab] = useState('profile');
  const [payments, setPayments] = useState([]);
  const LogActivity = useLogActivity();

  useFetchPayments(setUserData, setName, setSurname, setAddress, 
    setEmailValidated, setValidationDate, setPayments);

  const handleEditToggle = () => {
    setEditMode(!editMode);
  };

  const handleSave = () => {
    axios.post(URL_API + URL_UPDATE_PROFILE, { name, surname, address })
      .then(response => {
        setUserData({ ...userData, name, surname, address });
        setEditMode(false);
      })
      .catch(error => {
        console.error('Error updating user data', error);
      });
  };

  return (
    <div className="upload-form-container">
      <HeaderPlateforme 
        handleMenuClick={handleMenuClick}
      />
      <div className="menu-bar">
        <button className={activeTab === 'profile' ? 'active' : ''} onClick={() => {setActiveTab('profile'); LogActivity("click_profile_menu", "")}}>{t("plateforme.profilesettings.profilebutton")}</button>
        <button className={activeTab === 'billing' ? 'active' : ''} onClick={() => {setActiveTab('billing'); LogActivity("click_billing_menu", "")}}>{t("plateforme.profilesettings.billingbutton")}</button>
      </div>
      <div className='profile-container'>
      {activeTab === 'profile' && (
        <div >
          <div className="profile-section">
            <h2>{t("plateforme.profilesettings.profiletitle")}</h2>
            <div className="profile-item">
              <label>{t("overall.email")}:</label>
              <span>{userData.email}</span>
              <span className={`validation-status ${emailValidated ? 'validated' : 'not-validated'}`}>
                {emailValidated ? `${t("plateforme.profilesettings.validatedemail")} ${new Date(validationDate).toLocaleDateString()}` : t("plateforme.profilesettings.notvalidatedemail")}
              </span>
            </div>
            <div className="profile-item">
              <label>{t("overall.name")}:</label>
              {editMode ? (
                <input type="text" value={name} onChange={(e) => setName(e.target.value)} />
              ) : (
                <span>{userData.name}</span>
              )}
            </div>
            <div className="profile-item">
              <label>{t("overall.surname")}:</label>
              {editMode ? (
                <input type="text" value={surname} onChange={(e) => setSurname(e.target.value)} />
              ) : (
                <span>{userData.surname}</span>
              )}
            </div>
            <div className="profile-item">
              <label>{t("overall.address")}:</label>
              {editMode ? (
                <input type="text" value={address} onChange={(e) => setAddress(e.target.value)} />
              ) : (
                <span>{userData.address || 'No address provided'}</span>
              )}
            </div>
            <div className="profile-item">
              <label>{t("overall.creationdate")}:</label>
              <span>{new Date(userData.creation_date).toLocaleDateString()}</span>
            </div>
            <div className="profile-actions">
              {editMode ? (
                <button onClick={handleSave}>{t("plateforme.profilesettings.save")}</button>
              ) : (
                <button onClick={handleEditToggle}>{t("plateforme.profilesettings.edit")}</button>
              )}
            </div>
          </div>
        </div>
      )}
      {activeTab === 'billing' && <BillingSettings payments={payments} t={t}/>}
      </div>
    </div>
  );
}
export default ProfileSettings;
