import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Header from './components/Header';
import Login from './components/Login';
import Signup from './components/Signup';
import Sidebar from './components/Sidebar';
import UploadForm from './components/UploadForm';
import Result from './components/Result';
import PrivateRoute from './components/PrivateRoute';

import './css/packages/bootstrap.min.css';

function App() {
  const [file, setFile] = useState(null);
  const [text, setText] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmission = (file, text) => {
    setFile(file);
    setText(text);
    setSubmitted(true);
  };
  return (
    <Router>
      <div>
        <Header />
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <div style={{ display: 'flex' }}>
                  <Sidebar onSubmit={handleSubmission} />
                  <UploadForm file={file} text={text} submitted={submitted} />
                </div>
              </PrivateRoute>
            }
          />
          <Route
            path="/result"
            element={
              <PrivateRoute>
                <Result />
              </PrivateRoute>
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;