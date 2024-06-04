import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Card from './Card';
import '../utils/utils_knn';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch, faSort, faCalendarAlt, faDollarSign, faMapMarkerAlt } from '@fortawesome/free-solid-svg-icons';
import {URL_API_BACK, URL_GET_TASK, URL_API, URL_GET_IDS_INFO, CARDS_PER_PAGE, URL_UPLOAD} from '../utils/constants';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js';

import '../css/UploadForm.css';

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend);

function UploadForm({
  setFile,
  setText,
  setTaskId,
  taskId,
  file,
  text,
  result,
  setResult,
  botresult,
  setBotResult,
  chatBotResultFetched,
  setChatBotResultFetched,
  additionalData,
  setAdditionalData,
  avgMinEstimates,
  avgMaxEstimates,
  setAvgMaxEstimates,
  setAvgMinEstimates,
  avgFinalResult,
  setAvgFinalResult
}) {
  
  const [currentPage, setCurrentPage] = useState(1);
  const [analysisInProgress, setAnalysisInProgress] = useState(false);
  const [sortOrder, setSortOrder] = useState('distance');
  const [dropdownOpen, setDropdownOpen] = useState(false);
  
  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };

  const handleSortChange = (newSortOrder) => {
    setSortOrder(newSortOrder);
    setDropdownOpen(false)
  };

  const sortData = (data, sortOrder) => {
    switch (sortOrder) {
      case 'date':
        return data.sort((a, b) => new Date(b.date) - new Date(a.date));
      case 'final_price':
        return data.sort((a, b) => b.final_result - a.final_result);
      case 'distance':
      default:
        return data.sort((a, b) => a.distances - b.distances);
    }
  };

  const sortedData = sortData([...additionalData], sortOrder);

  const paginatedData = sortedData.slice(
    (currentPage - 1) * CARDS_PER_PAGE,
    currentPage * CARDS_PER_PAGE
  );

  const totalPages = Math.ceil(additionalData.length / CARDS_PER_PAGE);

  const handleSearchFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSearchTextChange = (e) => {
    setText(e.target.value);
  };

  const handleSearchSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    if (file) {
      formData.append('file', file);
    }
    if (text) {
      formData.append('text', text);
    }
    
    try {
      const response = await axios.post(URL_API_BACK + URL_UPLOAD, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      const task_id = response.data.task_id;
      console.log(task_id);

      setFile(file);
      setText(text);
      setBotResult(null)
      setChatBotResultFetched(false);
      setAnalysisInProgress(true);
      setTaskId(task_id);
      setResult(null);
      setAdditionalData([]);
      setAvgMinEstimates(0);
      setAvgMaxEstimates(0);
      setAvgFinalResult(0);
    } catch (error) {
      console.error('Error uploading file', error);
    }
  };
  
  useEffect(() => {
    if (taskId && analysisInProgress) {
      const interval = setInterval(async () => {
        try {
          const response = await axios.get(URL_API_BACK + URL_GET_TASK + '/' + taskId);
          if (response.data.state === 'SUCCESS') {
            setResult(response.data.result);
            clearInterval(interval);
            setAnalysisInProgress(false);
            console.log(response.data)
          }
        } catch (error) {
          console.error('Error fetching task result', error);
        }
      }, 2000); // Poll every X sec
      return () => clearInterval(interval);
    }
  }, [taskId, analysisInProgress]);

  useEffect(() => {
    if (result && result.image && result.image.ids) {
      const fetchData = async () => {
        try {
          const ids = result.image.ids.flat();
          const distances = result.image.distances.flat();
          const response = await axios.post(URL_API + URL_GET_IDS_INFO, 
              {'ids': ids,
                'distances': distances
              });

          // Ensure response.data is an array
          if (Array.isArray(response.data.result)) {

            setAdditionalData(response.data.result);
            setAvgMinEstimates(response.data.min_estimate);
            setAvgMaxEstimates(response.data.max_estimate);
            setAvgFinalResult(response.data.final_result);

          } else {
            console.error('Unexpected response format:', response.data);
          }
        } catch (error) {
          console.error('Error fetching additional data', error);
        }
      };
      fetchData();
    }
  }, [result]);

  useEffect(() => {
    if (result && result.image && result.image.documents && !chatBotResultFetched) {
      const fetchLLM = async () => {
        try {
          const art_pieces = result.image.documents.flat();
          const response = await axios.post(URL_API_BACK + '/chatbot', {art_pieces: art_pieces});
          setBotResult(response.data.result)
          setChatBotResultFetched(true);
        } catch (error) {
          console.error('Error fetching additional data', error);
        }
      };
      fetchLLM(); 
    }
  }, [result, chatBotResultFetched]);

  return (
    <div className="upload-form-container">
      {!taskId ? (
        <div>
          <h2>Welcome to Art Analytics</h2>
          <p>Our solution provides detailed analysis of artwork through image and text inputs.</p>
            <div className="search-area">
              <form onSubmit={handleSearchSubmit} className="search-form">
                <FontAwesomeIcon icon={faSearch} className="search-icon" />
                <input 
                  type="text" 
                  value={text} 
                  onChange={handleSearchTextChange} 
                  placeholder="Enter description" 
                  className="search-input" 
                />
                <input 
                  type="file" 
                  onChange={handleSearchFileChange} 
                  className="search-file-input" 
                />
                <button type="submit" className="search-submit-button">Send for Analysis</button>
              </form>
            </div>
        </div>
      ) : (
        <div className="result-container">
          <div className="summary-area">
            <div className="part1">
                <div className="part-header common-title">
                    <h2>Estimation</h2>
                </div>
                <div className="part-content">
                  <div className="left">
                    {file && <img src={URL.createObjectURL(file)} alt="Uploaded" className="summary-image" />}
                  </div>
                  <div className="middle">
                    {botresult &&<p><strong>Designation:</strong> {botresult}</p>}
                    <div className="card-footer">
                      <span className="card-price"><strong>Estimate:</strong> {avgMinEstimates}-{avgMaxEstimates} €</span>
                      <span className="card-result"><strong>Final:</strong> {avgFinalResult} €</span>
                    </div>
                  </div>
                </div>
                <div className="search-area">
                  <form onSubmit={handleSearchSubmit} className="search-form">
                    <FontAwesomeIcon icon={faSearch} className="search-icon" />
                    <input 
                      type="text" 
                      value={text} 
                      onChange={handleSearchTextChange} 
                      placeholder="Enter description" 
                      className="search-input" 
                    />
                    <input 
                      type="file" 
                      onChange={handleSearchFileChange} 
                      className="search-file-input" 
                    />
                    <button type="submit" className="search-submit-button">Send for Analysis</button>
                  </form>
                </div>
            </div>
            <div className="part2">
            </div>
          </div>
          <div className="delimiter-line"></div>
          {additionalData.length > 0 ? (
            <div className="additional-data">
              <div className="pagination">
                {Array.from({ length: totalPages }, (_, index) => (
                  <button
                    key={index + 1}
                    className={`pagination-button ${currentPage === index + 1 ? 'active' : ''}`}
                    onClick={() => handlePageChange(index + 1)}
                  >
                    {index + 1}
                  </button>
                ))}
                <div className="sort-buttons">
                <div className="dropdown">
                  <button onClick={() => setDropdownOpen(!dropdownOpen)} className="dropbtn">
                    <FontAwesomeIcon icon={faSort} /> Sort
                  </button>
                  {dropdownOpen && (
                    <div className="dropdown-content">
                      <button onClick={() => handleSortChange('distance')} className={`sort-button ${sortOrder === 'distance' ? 'active' : ''}`}>
                        <FontAwesomeIcon icon={faMapMarkerAlt} /> Relevance
                      </button>
                      <button onClick={() => handleSortChange('date')} className={`sort-button ${sortOrder === 'date' ? 'active' : ''}`}>
                        <FontAwesomeIcon icon={faCalendarAlt} /> Date
                      </button>
                      <button onClick={() => handleSortChange('final_price')} className={`sort-button ${sortOrder === 'final_price' ? 'active' : ''}`}>
                        <FontAwesomeIcon icon={faDollarSign} /> Final Price
                      </button>
                    </div>
                  )}
                </div>
              </div>
              </div>
              <div className="card-container">
                {paginatedData.map((item, index) => (
                  <Card key={index} item={item} />
                ))}
              </div>
            </div>
          ) : (
            <p>No additional data available</p>
          )}
          <div className="pagination">
            {Array.from({ length: totalPages }, (_, index) => (
              <button
                key={index + 1}
                className={`pagination-button ${currentPage === index + 1 ? 'active' : ''}`}
                onClick={() => handlePageChange(index + 1)}
              >
                {index + 1}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default UploadForm;