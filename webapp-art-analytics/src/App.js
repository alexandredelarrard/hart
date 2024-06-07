import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Login from './components/Login';
import Signup from './components/Signup';
import Sidebar from './components/Sidebar';
import UploadForm from './components/UploadForm';
import OptimizeSale from './components/OptimizeSale';
import Home from './components/Home';
import ArtIdentify from './components/ArtIdentify';
import PrivateRoute from './components/PrivateRoute';
import CardDetail from './components/CardDetail';
import './css/packages/bootstrap.min.css';

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
  const [activeMenu, setActiveMenu] = useState('closest-lots');

  const handleMenuClick = (menu) => {
    setActiveMenu(menu);
  };

  const renderContent = () => {
    switch (activeMenu) {
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
        />
        );
      case 'optimize-sale':
        return <OptimizeSale />;
      case 'authentify-art':
        return <ArtIdentify />;
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
          <Route
            path="/analytics"
            element={
              <PrivateRoute>
                <div style={{ display: 'flex' }}>
                  <Sidebar onMenuClick={handleMenuClick} />
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