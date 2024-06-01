import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Card from './Card';
import { Pie } from 'react-chartjs-2';
import {URL_API_BACK, URL_GET_TASK, URL_API, URL_GET_IDS_INFO, CARDS_PER_PAGE} from '../utils/constants';
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
  taskId,
  file,
  text,
  result,
  setResult,
  additionalData,
  setAdditionalData,
  avgEstimates,
  setAvgEstimates,
  avgFinalResult,
  setAvgFinalResult
}) {
  const [currentPage, setCurrentPage] = useState(1);
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [
      {
        data: [],
        backgroundColor: []
      }
    ]
  });

  useEffect(() => {
    if (taskId) {
      const interval = setInterval(async () => {
        try {
          const response = await axios.get(URL_API_BACK + URL_GET_TASK + '/' + taskId);
          if (response.data.state === 'SUCCESS') {
            setResult(response.data.result);
            clearInterval(interval);
            console.log(response.data)
          }
        } catch (error) {
          console.error('Error fetching task result', error);
        }
      }, 1000); // Poll every X sec
      return () => clearInterval(interval);
    }
  }, [taskId]);

  useEffect(() => {
    if (result && result.image && result.image.ids) {
      const fetchData = async () => {
        try {
          const ids = result.image.ids.flat();
          const response = await axios.post(URL_API + URL_GET_IDS_INFO, 
              {'ids': ids});

          // Ensure response.data is an array
          if (Array.isArray(response.data)) {

            setAdditionalData(response.data);

            // Calculate averages
            const avgEstimates = response.data.reduce((acc, item) => acc + (item.estimate_min + item.estimate_max) / 2, 0) / response.data.length;
            const avgFinalResult = response.data.reduce((acc, item) => acc + item.final_result, 0) / response.data.length;
            console.log(avgFinalResult)

            setAvgEstimates(avgEstimates);
            setAvgFinalResult(avgFinalResult);

            // Prepare chart data
             // Prepare chart data
             const localizationCounts = response.data.reduce((acc, item) => {
              acc[item.localisation] = (acc[item.localisation] || 0) + 1;
              return acc;
            }, {});

            // Sort locations by count
            const sortedLocations = Object.entries(localizationCounts).sort(
              (a, b) => b[1] - a[1]
            );

            // Limit to top 5 locations and group the rest as "Other"
            const topLocations = sortedLocations.slice(0, 7);
            const otherLocations = sortedLocations.slice(7);

            const topLabels = topLocations.map((location) => location[0]);
            const topData = topLocations.map((location) => location[1]);

            if (otherLocations.length > 0) {
              topLabels.push('Other');
              topData.push(
                otherLocations.reduce((acc, location) => acc + location[1], 0)
              );
            }

            const newChartData = {
              labels: topLabels,
              datasets: [
                {
                  data: topData,
                  backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF',
                    '#FF9F40'
                  ]
                }
              ]
            };

            setChartData(newChartData);
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

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };

  const paginatedData = additionalData.slice(
    (currentPage - 1) * CARDS_PER_PAGE,
    currentPage * CARDS_PER_PAGE
  );

  const totalPages = Math.ceil(additionalData.length / CARDS_PER_PAGE);

  return (
    <div className="upload-form-container">
      {!taskId ? (
        <div>
          <h2>Welcome to Art Analytics</h2>
          <p>Our solution provides detailed analysis of artwork through image and text inputs.</p>
        </div>
      ) : (
        <div className="result-container">
          <div className="summary-area">
            <div className="left">
              {file && <img src={URL.createObjectURL(file)} alt="Uploaded" className="summary-image" />}
            </div>
            <div className="middle">
              {text && <p>{text}</p>}
              <p><strong>Average Estimate:</strong> {avgEstimates.toFixed(2)}</p>
              <p><strong>Average Final Result:</strong> {avgFinalResult.toFixed(2)}</p>
            </div>
            <div className="right">
              {chartData.labels.length > 0 ? (
                <Pie data={chartData} />
              ) : (
                <p>No data available for chart</p>
              )}
            </div>
          </div>
          {additionalData.length > 0 ? (
            <div className="additional-data">
              <h3>Sold past Lot</h3>
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