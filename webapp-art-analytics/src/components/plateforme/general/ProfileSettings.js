import React, { useState, useEffect} from 'react';
import Cookies from 'js-cookie';
import { ModifyProfile } from '../../../hooks/plateforme/ModifyProfile.js';
import { useNavigate } from 'react-router-dom';
import { checkAuth } from '../../../hooks/general/identification.js';

function ProfileSettings({
  userData,
  setUserData,
  t
}) {
  const [editMode, setEditMode] = useState(false);
  const [name, setName] = useState('');
  const [surname, setSurname] = useState('');
  const [address, setAddress] = useState('');
  const [emailValidated, setEmailValidated] = useState(false);
  const [validationDate, setValidationDate] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const isAuthenticated = checkAuth();
    const userdataCookie = Cookies.get('userdata');

    if(isAuthenticated){
        if (userdataCookie) {
        const parsedUserdata = JSON.parse(userdataCookie);

        setUserData(parsedUserdata);
        setName(parsedUserdata.name);
        setSurname(parsedUserdata.surname);
        setAddress(parsedUserdata.address || '');
        setEmailValidated(parsedUserdata.emailValidated || false);
        setValidationDate(parsedUserdata.creation_date || null);
        }
  } else {
    navigate("/login");
  }
  }, [setUserData, setName, setSurname, setAddress, setEmailValidated, setValidationDate]);

  const handleEditToggle = () => {
    setEditMode(!editMode);
  };

  const handleSave = async () => {
    try {
      await ModifyProfile(name, surname, address);

      const newUserData = { ...userData, name, surname, address };
      setUserData(newUserData);
      setEditMode(false);
      Cookies.set('userdata', JSON.stringify(newUserData));
    } catch (error) {
      console.error('Error updating user data', error);
    }
  };

  return (
    <div className="profile-container">
        <div className='login-form'>
            <div className="profile-section">
            <h2>{t("plateforme.profilesettings.profiletitle")}</h2>
            <div className="form-group">
                <label>{t("overall.email")}:
                <span className={`validation-status ${emailValidated ? 'validated' : 'not-validated'}`}>
                    {emailValidated ? `${t("plateforme.profilesettings.validatedemail")} ${new Date(validationDate).toLocaleDateString()}` : t("plateforme.profilesettings.notvalidatedemail")}
                </span>
                </label>
                <input
                    type="text"
                    value={userData.email}
                    disabled
                />
            </div>
            <div className="form-group">
                <label>{t("overall.name")}:</label>
                <input
                    type="text"
                    value={editMode ? name : userData.name}
                    onChange={(e) => setName(e.target.value)}
                    disabled = {editMode ? false: true}
                />
            </div>
            <div className="form-group">
                <label>{t("overall.surname")}:</label>
                <input
                    type="text"
                    value={editMode ? surname : userData.surname}
                    onChange={(e) => setSurname(e.target.value)}
                    disabled = {editMode ? false: true}
                />
            </div>
            <div className="form-group">
                <label>{t("overall.address")}:</label>
                <input
                    type="text"
                    value={editMode ? address : userData.address}
                    onChange={(e) => setAddress(e.target.value)}
                    disabled = {editMode ? false: true}
                />
            </div>
            <div className="form-group">
                <label>{t("overall.creationdate")}:</label>
                <input
                    type="text"
                    value={new Date(userData.creation_date).toLocaleDateString()}
                    disabled
                />
            </div>
                {editMode ? (
                <button onClick={handleSave} className="login-button">{t("plateforme.profilesettings.save")}</button>
                ) : (
                <button onClick={handleEditToggle} className="login-button">{t("plateforme.profilesettings.edit")}</button>
                )}
            </div>
        </div>
    </div>
  );
}
export default ProfileSettings;
