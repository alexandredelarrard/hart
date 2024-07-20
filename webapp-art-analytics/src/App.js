import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

import './css/packages/bootstrap.min.css';

import Sidebar from './components/plateforme/Sidebar';
import UploadForm from './components/plateforme/UploadForm';
import OptimizeSale from './components/plateforme/OptimizeSale';
import SearchArt from './components/plateforme/SearchArt';
import ArtIdentify from './components/plateforme/ArtIdentify';
import CardDetail from './components/plateforme/upload_utils/CardDetail';
import Settings from './components/plateforme/Settings';
import Offers from './components/plateforme/Offers';
import HeaderPlateforme from "./components/plateforme/upload_utils/HeaderPlateforme.js";

import Home from './components/Home';
// import Trial from './components/landing_page/Trial';
import ContactUs from './components/landing_page/ContactUs';
import Terms from './components/landing_page/Terms';
import CGV from './components/landing_page/CGV';
import About from './components/landing_page/About';
// import Checkout from './components/landing_page/Checkout';
import ComingSoon from './components/landing_page/ComingSoon.js';

import Login from './components/connectors/Login';
// import ResetPassword from './components/connectors/ResetPassword';
import SetNewPassword from './components/connectors/SetNewPassword';
import ProtectedRoute from './components/connectors/ProtectedRoute';
import Confirm from './components/connectors/Confirm';
import {PATHS} from "./utils/constants.js"

import './App.css';
import './i18n';


function App() {

  const { i18n } = useTranslation();

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
  };

  const [userData, setUserData] = useState({});
  const [uploadFormState, setUploadFormState] = useState({
    searchfile: '',
    searchtext: '',
    file: '',
    text: '',
    taskId: null,
    result: null,
    botresult: null,
    additionalData: [],
    avgMinEstimates: 0,
    avgMaxEstimates: 0,
    avgFinalResult: 0,
    chatBotResultFetched: false,
    analysisInProgress: false,
    newResultSaved: false,
    experts: [],
    minPrice: '',
    maxPrice: '',
    minDate: '',
    maxDate: '',
    activeMenu: 'search-art',
    activeLi: '',
    showResults: false
  });

  const [searchArtState, setSearchArtState] = useState({
    searchResults: [],
    trendData: null,
  });

  const [planExpired, setPlanExpired] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const { t } = useTranslation();

  const updateUploadFormState = (newState) => {
    setUploadFormState((prevState) => ({ ...prevState, ...newState }));
  };

  const uploadFormHandlers = {
    setSearchFile: (searchfile) => updateUploadFormState({searchfile}),
    setSearchText: (searchtext) => updateUploadFormState({searchtext}),
    setFile: (file) => updateUploadFormState({file}),
    setText: (text) => updateUploadFormState({text}),
    setTaskId: (taskId) => updateUploadFormState({ taskId }),
    setResult: (result) => updateUploadFormState({ result }),
    setBotResult: (botresult) => updateUploadFormState({ botresult }),
    setChatBotResultFetched: (chatBotResultFetched) => updateUploadFormState({ chatBotResultFetched }),
    setAdditionalData: (additionalData) => updateUploadFormState({ additionalData }),
    setAvgMaxEstimates: (avgMaxEstimates) => updateUploadFormState({ avgMaxEstimates }),
    setAvgMinEstimates: (avgMinEstimates) => updateUploadFormState({ avgMinEstimates }),
    setAvgFinalResult: (avgFinalResult) => updateUploadFormState({ avgFinalResult }),
    setAnalysisInProgress: (analysisInProgress) => updateUploadFormState({ analysisInProgress }),
    setMinPrice: (minPrice) => updateUploadFormState({ minPrice }),
    setMaxPrice: (maxPrice) => updateUploadFormState({ maxPrice }),
    setMinDate: (minDate) => updateUploadFormState({ minDate }),
    setMaxDate: (maxDate) => updateUploadFormState({ maxDate }),
    setNewResultSaved: (newResultSaved) => updateUploadFormState({ newResultSaved }),
    setExperts: (experts) => updateUploadFormState({experts}),
    setActiveMenu : (activeMenu) => updateUploadFormState({activeMenu}),
    setActiveLi : (activeLi) => updateUploadFormState({activeLi}),
    setShowResults : (showResults) => updateUploadFormState({showResults}),
  };

  const updateSearchArtState = (newState) => {
    setSearchArtState((prevState) => ({ ...prevState, ...newState }));
  };

  const searchArtHandlers = {
    setSearchResults: (searchResults) => updateSearchArtState({ searchResults }),
    setTrendData: (trendData) => updateSearchArtState({ trendData }),
  };

  const renderContent = () => {
    switch (uploadFormState.activeMenu) {
      case 'search-art':
        return <SearchArt
                searchArtState={searchArtState}
                searchArtHandlers={searchArtHandlers}
                setPlanExpired={setPlanExpired}
                planExpired={planExpired}
                handleMenuClick={uploadFormHandlers.setActiveMenu}
                t={t}
              />;
      case 'closest-lots':
        return <UploadForm
                  uploadFormState={uploadFormState}
                  uploadFormHandlers={uploadFormHandlers}
                  setPlanExpired={setPlanExpired}
                  planExpired={planExpired}
                  i18n={i18n}
                  t={t}
              />;
      case 'optimize-sale':
        return <OptimizeSale t={t} />;
      case 'authentify-art':
        return <ArtIdentify t={t} />;
      case 'account-settings':
        return <Settings userData={userData} setUserData={setUserData} t={t} />;
      case 'my-offers':
        return <Offers t={t} />;
      default:
        return null;
    }
  };

  return (
    <Router>
      <div>
        <Routes>
          <Route path={PATHS["HOME"]} element={<Home scrolled={scrolled} setScrolled={setScrolled} changeLanguage={changeLanguage} t={t}/>} />
          <Route path={PATHS["LOGIN"]} element={<Login scrolled={true} t={t} changeLanguage={changeLanguage}/>} />
          {/* <Route path={PATHS["TRIAL"]} element={<Trial scrolled={true} t={t}/>} /> */}
          <Route path={PATHS["TRIAL"]} element={<ComingSoon changeLanguage={changeLanguage} scrolled={true} t={t}/>} />
          <Route path={PATHS["CONTACT"]} element={<ContactUs changeLanguage={changeLanguage} scrolled={true} t={t}/>} />
          <Route path={PATHS["ABOUT"]} element={<About changeLanguage={changeLanguage} scrolled={true} t={t}/>} />
          <Route path={PATHS["SOON"]} element={<ComingSoon changeLanguage={changeLanguage} scrolled={true} t={t}/>} />
          <Route path={PATHS["TERMS"]} element={<Terms changeLanguage={changeLanguage} scrolled={true} t={t}/>} />
          <Route path={PATHS["CGV"]} element={<CGV changeLanguage={changeLanguage} scrolled={true} t={t}/>} />
          {/* <Route path={PATHS["ENROLL"]} element={<Checkout scrolled={true} t={t}/>} /> */}
          <Route path={PATHS["ENROLL"]} element={<ComingSoon changeLanguage={changeLanguage} scrolled={true} t={t}/>} />
          {/* <Route path={PATHS["RESET_PWD"]} element={<ResetPassword changeLanguage={changeLanguage} scrolled={true} t={t}/>} /> */}
          <Route path={PATHS["RESET_PWD"]} element={<ComingSoon changeLanguage={changeLanguage} scrolled={true} t={t}/>} />
          <Route path={PATHS["CONFIRM_PWD"]} element={<Confirm changeLanguage={changeLanguage} scrolled={true} t={t}/>} />
          <Route path={PATHS["SET_NEW_PWD"]} element={<SetNewPassword changeLanguage={changeLanguage} scrolled={true} t={t}/>} />

          <Route
            path={PATHS["ANALYTICS"]}
            element={<ProtectedRoute />}>
              <Route
                path=""
                element={
                <div style={{ display: 'flex' }}>
                    <Sidebar
                      userData={userData}
                      setUserData={setUserData}
                      uploadFormHandlers={uploadFormHandlers}
                      uploadFormState={uploadFormState}
                      t={t}
                    />
                    <div className="upload-form-container">
                      <HeaderPlateforme
                        changeLanguage={changeLanguage}
                        handleMenuClick={uploadFormHandlers.setActiveMenu}
                        t={t}
                      />
                      {renderContent()}
                    </div>
                </div>
              }
              />
          </Route>
          <Route
            path={PATHS["CARD_ID"]}
            element={<ProtectedRoute />}>
            <Route
              path=""
              element={
                  <div style={{ display: 'flex' }}>
                    <CardDetail
                      i18n={i18n}
                      t={t}/>
                  </div>
              }
            />
          </Route>
        </Routes>
      </div>
    </Router>
  );
}

export default App;
