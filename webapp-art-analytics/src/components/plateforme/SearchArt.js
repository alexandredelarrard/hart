import React, { useEffect, useState } from 'react';
import Cookies from 'js-cookie';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, BarElement } from 'chart.js';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import Card from './upload_utils/Card.js';
import { useNavigate } from 'react-router-dom';
import HeaderPlateforme from "./upload_utils/HeaderPlateforme.js";
import SearchBar from './search_utils/SearchBar.js';
import * as d3 from 'd3';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend);

function SearchArt({ 
  setPlanExpired, 
  planExpired, 
  handleMenuClick, 
  searchResults,
  setSearchResults,
  trendData,
  setTrendData,
  t }) {
  const [searchText, setSearchText] = useState('');
  const [mapData, setMapData] = useState([]);
  const [searchVolumeExpired, setsearchVolumeExpired] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    const remaining_search_volume = Cookies.get('remaining_search_volume');
    const plan_end_date = Cookies.get('plan_end_date');

    if (plan_end_date) {
      const planEndDate = new Date(plan_end_date);
      const currentDate = new Date();
      if (currentDate > planEndDate) {
        setPlanExpired(true);
      }
      if (0 >= remaining_search_volume) {
        setsearchVolumeExpired(true);
      }
    }
  }, [setPlanExpired, setsearchVolumeExpired]);

  useEffect(() => {
    if (searchResults.length > 0) {
      // Aggregate data by month and calculate median
      const dataByMonth = d3.rollup(
        searchResults,
        v => ({
          percentile25: d3.quantile(v.map(d => d.final_result).sort(d3.ascending), 0.25),
          volume: v.length
        }),
        d => d3.timeMonth(new Date(d.date))
      );

      const sortedData = Array.from(dataByMonth).sort((a, b) => a[0] - b[0]);

      const dates = sortedData.map(d => d3.timeFormat("%Y-%m")(d[0]));
      const percentiles = sortedData.map(d => d[1].percentile25);
      const volumes = sortedData.map(d => d[1].volume);

      setTrendData({
        labels: dates,
        datasets: [
          {
            type: 'line',
            label: 'Median Final Result Per Month',
            data: percentiles,
            borderColor: 'rgba(75,192,192,1)',
            backgroundColor: 'rgba(75,192,192,0.2)',
            fill: false,
            yAxisID: 'y1',
          },
          {
            type: 'bar',
            label: 'Volume of Sales Per Month',
            data: volumes,
            borderColor: 'rgba(0,0,255,0.5)',
            backgroundColor: 'rgba(0,0,255,0.5)',
            fill: true,
            yAxisID: 'y2',
          },
        ],
      });

      const localisationCounts = searchResults.reduce((acc, result) => {
        acc[result.localisation] = (acc[result.localisation] || 0) + 1;
        return acc;
      }, {});

      setMapData(Object.entries(localisationCounts).map(([localisation, count]) => ({
        localisation,
        count,
      })));
    }
  }, [searchResults]);

  return (
    <div className="upload-form-container">
      <HeaderPlateforme handleMenuClick={handleMenuClick} />
      <h2>{t("plateforme.searchart.searchtitle")}</h2>
      <SearchBar
        searchText={searchText}
        setSearchText={setSearchText}
        setSearchResults={setSearchResults}
        planExpired={planExpired}
        searchVolumeExpired={searchVolumeExpired}
        handleMenuClick={handleMenuClick}
        t={t}
      />
    <div className="result-container">
        {trendData && (
          <div className="summary-area">
            <div className="part1-search">
              <div className="part-content">
                <Line 
                  data={trendData} 
                  options={{
                    scales: {
                      y1: {
                        type: 'linear',
                        position: 'left',
                        title: {
                          display: true,
                          text: '25th Percentile of Final Results'
                        },
                      },
                      y2: {
                        type: 'linear',
                        position: 'right',
                        title: {
                          display: true,
                          text: 'Volume of Sales'
                        },
                        grid: {
                          drawOnChartArea: false,
                        },
                      },
                    },
                  }}
                />
              </div>
            </div>
            <div className="part2-search">
              <div className="part-content">
                <MapContainer center={[51.505, -0.09]} zoom={2} style={{ height: '100%', width: '100%' }}>
                  <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  />
                  {/* {mapData.map((data, index) => (
                    <CircleMarker
                      key={index}
                      center={[data.localisation.lat, data.localisation.lng]}
                      radius={Math.log(data.count) * 2}
                      fillOpacity={0.5}
                    >
                      <Popup>
                        {data.localisation}: {data.count} sales
                      </Popup>
                    </CircleMarker>
                  ))} */}
                </MapContainer>
              </div>
            </div>
          </div>
        )}
      <div className="delimiter-line"></div>
      {searchResults.length > 0 ? (
        <div className="additional-data">
          <div className="card-container">
            {searchResults.map((item, index) => (
              <Card key={index} item={item} t={t} />
            ))}
          </div>
          </div>) : (
          <></>
        )}
    </div>
  </div>
  );
}

export default SearchArt;