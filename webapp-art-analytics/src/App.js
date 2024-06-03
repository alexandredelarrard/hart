import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Login from './components/Login';
import Sidebar from './components/Sidebar';
import UploadForm from './components/UploadForm';
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
  const [avgEstimates, setAvgEstimates] = useState(0);
  const [avgFinalResult, setAvgFinalResult] = useState(0);

  const handleTaskSubmit = (taskId, file, text) => {
    setFile(file);
    setText(text);
    setTaskId(taskId);
    setResult(null); // Reset result to trigger fetching new data
    setAdditionalData([]);
    setAvgEstimates(0);
    setAvgFinalResult(0);
  };

  return (
    <Router>
      <div>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <div style={{ display: 'flex' }}>
                  <Sidebar onTaskSubmit={handleTaskSubmit} />
                  <UploadForm 
                    taskId={taskId}
                    file={file}
                    text={text}
                    result={result}
                    setResult={setResult}
                    botresult={botresult}
                    setBotResult={setBotResult}
                    additionalData={additionalData}
                    setAdditionalData={setAdditionalData}
                    avgEstimates={avgEstimates}
                    setAvgEstimates={setAvgEstimates}
                    avgFinalResult={avgFinalResult}
                    setAvgFinalResult={setAvgFinalResult}
                  />
                </div>
              </PrivateRoute>
            }
          />
           <Route
            path="/card/:id"
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