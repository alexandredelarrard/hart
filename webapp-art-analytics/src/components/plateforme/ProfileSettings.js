import React, { useState, useEffect } from 'react';
import Cookies from 'js-cookie';
import axios from 'axios';
import { logActivity } from '../../utils/activity.js';
import HeaderPlateforme from "../landing_page/HeaderPlateforme.js";
import PaymentTable from "../plateforme/form_components/PaymentTable.js"
import {URL_GET_PAYMENTS, URL_API, URL_UPDATE_PROFILE} from "../../utils/constants.js";

import '../../css/ProfileSettings.css';

function ProfileSettings({handleMenuClick}) {
  const [userData, setUserData] = useState({});
  const [editMode, setEditMode] = useState(false);
  const [name, setName] = useState('');
  const [surname, setSurname] = useState('');
  const [address, setAddress] = useState('');
  const [emailValidated, setEmailValidated] = useState(false);
  const [validationDate, setValidationDate] = useState(null);
  const [activeTab, setActiveTab] = useState('profile');
  const [payments, setPayments] = useState([]);

  useEffect(() => {
    const token = Cookies.get('token');
    if (!token) {
      return;
    }

    const userdataCookie = Cookies.get('userdata');
    if (userdataCookie) {
      const parsedUserdata = JSON.parse(userdataCookie);
      setUserData(parsedUserdata);
      setName(parsedUserdata.name);
      setSurname(parsedUserdata.surname);
      setAddress(parsedUserdata.address || '');
      setEmailValidated(parsedUserdata.emailValidated || false);
      setValidationDate(parsedUserdata.creation_date || null);

      axios.get(`${URL_API + URL_GET_PAYMENTS}?user_id=${parsedUserdata.id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )
      .then(response => {
        setPayments(response.data.results); 
      })
      .catch(error => {
          console.error('Error fetching former results:', error);
      });
    }
  }, []);

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
        <button className={activeTab === 'profile' ? 'active' : ''} onClick={() => {setActiveTab('profile'); logActivity("click_profile_menu", "")}}>Profile</button>
        <button className={activeTab === 'billing' ? 'active' : ''} onClick={() => {setActiveTab('billing'); logActivity("click_billing_menu", "")}}>Billing</button>
      </div>
      <div className='profile-container'>
      {activeTab === 'profile' && (
        <div >
          <div className="profile-section">
            <h2>Account Settings</h2>
            <div className="profile-item">
              <label>Email:</label>
              <span>{userData.email}</span>
              <span className={`validation-status ${emailValidated ? 'validated' : 'not-validated'}`}>
                {emailValidated ? `Validated on ${new Date(validationDate).toLocaleDateString()}` : 'Not validated'}
              </span>
            </div>
            <div className="profile-item">
              <label>Name:</label>
              {editMode ? (
                <input type="text" value={name} onChange={(e) => setName(e.target.value)} />
              ) : (
                <span>{userData.name}</span>
              )}
            </div>
            <div className="profile-item">
              <label>Surname:</label>
              {editMode ? (
                <input type="text" value={surname} onChange={(e) => setSurname(e.target.value)} />
              ) : (
                <span>{userData.surname}</span>
              )}
            </div>
            <div className="profile-item">
              <label>Address:</label>
              {editMode ? (
                <input type="text" value={address} onChange={(e) => setAddress(e.target.value)} />
              ) : (
                <span>{userData.address || 'No address provided'}</span>
              )}
            </div>
            <div className="profile-item">
              <label>Creation Date:</label>
              <span>{new Date(userData.creation_date).toLocaleDateString()}</span>
            </div>
            <div className="profile-actions">
              {editMode ? (
                <button onClick={handleSave}>Save</button>
              ) : (
                <button onClick={handleEditToggle}>Edit</button>
              )}
            </div>
          </div>
        </div>
      )}
      {activeTab === 'billing' && <BillingSettings payments={payments}/>}
      </div>
    </div>
  );
}

export default ProfileSettings;

function BillingSettings({payments}) {
  const [activePlan, setActivePlan] = useState('');

  useEffect(() => {
    const userdataCookie = Cookies.get('userdata');
    if (userdataCookie) {
      const parsedUserdata = JSON.parse(userdataCookie);
      setActivePlan(parsedUserdata.activeplan || 'free');
    }
  }, []);

  const plans = ['free', 'individuals', 'experts'];

  return (
    <div className="billing-section">
      <h2>Billing Settings</h2>
      <div className="plans">
        {plans.map(plan => (
          <div key={plan} className={`plan ${activePlan === plan ? 'active-plan' : ''}`}>
            <h3>{plan.charAt(0).toUpperCase() + plan.slice(1)}</h3>
            {activePlan === plan && <span className="current-plan">Current Plan</span>}
          </div>
        ))}
        <div className="">
            <PaymentTable payments={payments}/>
        </div>
      </div>
    </div>
  );
}