import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Login from './components/Login';
import Sidebar from './components/Sidebar';
import UploadForm from './components/UploadForm';
import PrivateRoute from './components/PrivateRoute';

import './css/packages/bootstrap.min.css';

function App() {
  const [file, setFile] = useState(null);
  const [text, setText] = useState('');
  const [taskId, setTaskId] = useState(null);

  const handleTaskSubmit = (taskId, file, text) => {
    setFile(file);
    setText(text);
    setTaskId(taskId);
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
                  <UploadForm taskId={taskId} file={file} text={text} />
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