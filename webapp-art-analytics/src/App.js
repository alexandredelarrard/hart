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

import Home from './components/Home';
import Trial from './components/landing_page/Trial';
import ContactUs from './components/landing_page/ContactUs';
import Terms from './components/landing_page/Terms';
import CGV from './components/landing_page/CGV';
import About from './components/landing_page/About';
import Checkout from './components/landing_page/Checkout';

import Login from './components/connectors/Login';
import ResetPassword from './components/connectors/ResetPassword';
import SetNewPassword from './components/connectors/SetNewPassword';
import Confirm from './components/connectors/Confirm';

import './i18n';

function App() {
  const [userData, setUserData] = useState({});
  const [file, setFile] = useState(null);
  const [text, setText] = useState('');
  const [taskId, setTaskId] = useState(null);
  const [result, setResult] = useState(null);
  const [botresult, setBotResult] = useState(null);
  const [additionalData, setAdditionalData] = useState([]);
  const [avgMinEstimates, setAvgMinEstimates] = useState(0);
  const [avgMaxEstimates, setAvgMaxEstimates] = useState(0);
  const [avgFinalResult, setAvgFinalResult] = useState(0);
  const [chatBotResultFetched, setChatBotResultFetched] = useState(false);
  const [analysisInProgress, setAnalysisInProgress] = useState(false);
  const [activeMenu, setActiveMenu] = useState('search-art');
  const [newResultSaved, setNewResultSaved] = useState(false);
  const [experts, setExperts] = useState([]);
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [minDate, setMinDate] = useState('');
  const [maxDate, setMaxDate] = useState('');
  const [scrolled, setScrolled] = useState(false);
  const [planExpired, setPlanExpired] = useState(false);
  const { t } = useTranslation();

  // SearchArt 
  const [searchResults, setSearchResults] = useState([]);
  const [trendData, setTrendData] = useState(null);

  const handleMenuClick = (menu) => {
    setActiveMenu(menu);
  };

  const renderContent = () => {
    switch (activeMenu) {
      case 'search-art':
        return <SearchArt 
                  setPlanExpired={setPlanExpired}
                  planExpired={planExpired}
                  handleMenuClick={handleMenuClick}
                  searchResults={searchResults}
                  setSearchResults={setSearchResults}
                  trendData={trendData}
                  setTrendData={setTrendData}
                  t={t}
              />;
      case 'closest-lots':
        return (
          <UploadForm 
            setFile={setFile}
            setText={setText}
            setTaskId={setTaskId}
            taskId={taskId}
            file={file}
            text={text}
            result={result}
            setResult={setResult}
            botresult={botresult}
            setBotResult={setBotResult}
            chatBotResultFetched={chatBotResultFetched}
            setChatBotResultFetched={setChatBotResultFetched}
            setAvgMaxEstimates={setAvgMaxEstimates}
            additionalData={additionalData}
            setAdditionalData={setAdditionalData}
            avgMaxEstimates={avgMaxEstimates}
            setAvgMinEstimates={setAvgMinEstimates}
            avgMinEstimates={avgMinEstimates}
            avgFinalResult={avgFinalResult}
            setAvgFinalResult={setAvgFinalResult}
            analysisInProgress={analysisInProgress}
            setAnalysisInProgress={setAnalysisInProgress}
            setNewResultSaved={setNewResultSaved}
            experts={experts}
            setExperts={setExperts}
            handleMenuClick={handleMenuClick} 
            setMinPrice={setMinPrice}
            setMaxPrice={setMaxPrice}
            setMinDate={setMinDate}
            setMaxDate={setMaxDate}
            minPrice={minPrice}
            maxPrice={maxPrice}
            minDate={minDate}
            maxDate={maxDate}
            setPlanExpired={setPlanExpired}
            planExpired={planExpired}
            t={t}
        />
        );
      case 'optimize-sale':
        return <OptimizeSale 
                handleMenuClick={handleMenuClick}
                t={t} 
              />;
      case 'authentify-art':
        return <ArtIdentify 
                handleMenuClick={handleMenuClick}
                t={t}
                />;
      case 'account-settings':
        return <Settings 
                  userData={userData}
                  setUserData={setUserData}
                  handleMenuClick={handleMenuClick}
                  t={t} 
                />;
      case 'my-offers':
        return <Offers 
                  handleMenuClick={handleMenuClick}
                  t={t} 
                />;
      default:
        return null;
    }
  };

  return (
    <Router>
      <div>
        <Routes>
          <Route path="/" element={<Home 
                                    scrolled={scrolled} 
                                    setScrolled={setScrolled} 
                                    t={t}/>} />
          <Route path="/login" element={<Login scrolled={true} t={t}/>} />
          <Route path="/trial" element={<Trial scrolled={true} t={t}/>} />
          <Route path="/contact" element={<ContactUs scrolled={true} t={t}/>} />
          <Route path="/about" element={<About scrolled={true} t={t}/>} />
          <Route path="/terms" element={<Terms scrolled={true} t={t}/>} />
          <Route path="/cgv" element={<CGV scrolled={true} t={t}/>} />
          <Route path="/enroll" element={<Checkout scrolled={true} t={t}/>} />
          <Route path="/reset-password" element={<ResetPassword scrolled={true} t={t}/>} />
          <Route path="/confirm/:token" element={<Confirm scrolled={true} t={t}/>} />
          <Route path="/set-new-password/:token" element={<SetNewPassword scrolled={true} t={t}/>} />
          <Route
            path="/analytics"
            element={
              <div style={{ display: 'flex' }}>
                <Sidebar 
                  userData={userData}
                  setUserData={setUserData}
                  onMenuClick={handleMenuClick} 
                  setFile={setFile}
                  setText={setText}
                  setTaskId={setTaskId}
                  analysisInProgress={analysisInProgress}
                  setResult={setResult}
                  setBotResult={setBotResult}
                  setChatBotResultFetched={setChatBotResultFetched}
                  setAvgMaxEstimates={setAvgMaxEstimates}
                  setAdditionalData={setAdditionalData}
                  setAvgMinEstimates={setAvgMinEstimates}
                  setAvgFinalResult={setAvgFinalResult}
                  setAnalysisInProgress={setAnalysisInProgress}
                  newResultSaved={newResultSaved}
                  setMinPrice={setMinPrice}
                  setMaxPrice={setMaxPrice}
                  setMinDate={setMinDate}
                  setMaxDate={setMaxDate}
                  t={t}
                />
                {renderContent()}
              </div>
            }
          />
           <Route
            path="/analytics/card/:id"
            element={
                <div style={{ display: 'flex' }}>
                  <CardDetail t={t}/>
                </div>
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;