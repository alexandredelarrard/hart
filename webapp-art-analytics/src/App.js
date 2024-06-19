import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

import './css/packages/bootstrap.min.css';

import Sidebar from './components/plateforme/Sidebar';
import UploadForm from './components/plateforme/UploadForm';
import OptimizeSale from './components/plateforme/OptimizeSale';
import SearchArt from './components/plateforme/SearchArt';
import ArtIdentify from './components/plateforme/ArtIdentify';
import CardDetail from './components/plateforme/utils/CardDetail';
import ProfileSettings from './components/plateforme/ProfileSettings';
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
  const [activeMenu, setActiveMenu] = useState('closest-lots');
  const [newResultSaved, setNewResultSaved] = useState(false);
  const [experts, setExperts] = useState([]);
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [minDate, setMinDate] = useState('');
  const [maxDate, setMaxDate] = useState('');
  const { t } = useTranslation();

  const handleMenuClick = (menu) => {
    setActiveMenu(menu);
  };

  const renderContent = () => {
    switch (activeMenu) {
      case 'search-art':
        return <SearchArt 
                  handleMenuClick={handleMenuClick} 
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
        return <ProfileSettings 
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
          <Route path="/" element={<Home t={t}/>} />
          <Route path="/login" element={<Login t={t}/>} />
          <Route path="/trial" element={<Trial t={t}/>} />
          <Route path="/contact" element={<ContactUs t={t}/>} />
          <Route path="/about" element={<About t={t}/>} />
          <Route path="/terms" element={<Terms t={t}/>} />
          <Route path="/cgv" element={<CGV t={t}/>} />
          <Route path="/enroll" element={<Checkout t={t}/>} />
          <Route path="/reset-password" element={<ResetPassword t={t}/>} />
          <Route path="/confirm/:token" element={<Confirm t={t}/>} />
          <Route path="/set-new-password/:token" element={<SetNewPassword t={t}/>} />
          <Route
            path="/analytics"
            element={
              <div style={{ display: 'flex' }}>
                <Sidebar 
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