import React from 'react';
import { useLocation } from 'react-router-dom';

function Result() {
  const location = useLocation();
  const { data } = location.state || {};

  return (
    <div>
      <h2>Result</h2>
      {data ? (
        <pre>{JSON.stringify(data, null, 2)}</pre>
      ) : (
        <p>No data available. Please upload a picture or text.</p>
      )}
    </div>
  );
}

export default Result;