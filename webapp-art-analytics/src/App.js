import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

import './css/packages/bootstrap.min.css';

import Sidebar from './components/plateforme/Sidebar';
import UploadForm from './components/plateforme/UploadForm';
import OptimizeSale from './components/plateforme/OptimizeSale';
import SearchArt from './components/plateforme/SearchArt';
import ArtIdentify from './components/plateforme/ArtIdentify';
import PrivateRoute from './components/plateforme/PrivateRoute';
import CardDetail from './components/plateforme/CardDetail';

import Home from './components/Home';
import Trial from './components/Trial';
import ProfileSettings from './components/ProfileSettings';
import Login from './components/Login';
import Signup from './components/Signup';
import ContactUs from './components/ContactUs';
import Terms from './components/Terms';
import CGV from './components/CGV';
import About from './components/About';
import Checkout from './components/Checkout';
import ResetPassword from './components/ResetPassword';
import SetNewPassword from './components/SetNewPassword';
import Confirm from './components/Confirm';

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

  const handleMenuClick = (menu) => {
    setActiveMenu(menu);
  };

  const renderContent = () => {
    switch (activeMenu) {
      case 'search-art':
        return <SearchArt 
                  handleMenuClick={handleMenuClick} 
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
            handleMenuClick={handleMenuClick} 
        />
        );
      case 'optimize-sale':
        return <OptimizeSale 
                handleMenuClick={handleMenuClick} 
              />;
      case 'authentify-art':
        return <ArtIdentify 
                handleMenuClick={handleMenuClick} />;
      case 'account-settings':
        return <ProfileSettings 
                handleMenuClick={handleMenuClick} 
                />;
      default:
        return null;
    }
  };

  return (
    <Router>
      <div>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/trial" element={<Trial />} />
          <Route path="/contact" element={<ContactUs />} />
          <Route path="/about" element={<About />} />
          <Route path="/terms" element={<Terms />} />
          <Route path="/cgv" element={<CGV />} />
          <Route path="/enroll" element={<Checkout />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/confirm/:token" element={<Confirm />} />
          <Route path="/set-new-password/:token" element={<SetNewPassword />} />
          <Route
            path="/analytics"
            element={
              <PrivateRoute>
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
                    newResultSaved={newResultSaved}
                    setAnalysisInProgress={setAnalysisInProgress}
                  />
                  {renderContent()}
                </div>
              </PrivateRoute>
            }
          />
           <Route
            path="/analytics/card/:id"
            element={
              <PrivateRoute>
                <div style={{ display: 'flex' }}>
                  <CardDetail />
                </div>
              </PrivateRoute>
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;