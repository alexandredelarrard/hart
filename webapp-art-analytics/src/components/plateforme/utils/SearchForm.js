import React from 'react';
import { useDropzone } from 'react-dropzone';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUpload, faSearch } from '@fortawesome/free-solid-svg-icons';
import "../../../css/SearchForm.css";
import { Link } from 'react-router-dom'; // Import Link for navigation

const SearchForm = ({ 
  planExpired, 
  closestVolumeExpired, 
  text, 
  handleSearchTextChange, 
  handleSearchSubmit, 
  handleSearchFileChange, 
  handleMenuClick
}) => {
  const onDrop = acceptedFiles => {
    handleSearchFileChange(acceptedFiles[0]);
  };

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    multiple: false,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png'],
    },
    disabled: planExpired || closestVolumeExpired // Disable dropzone if errors exist
  });

  const isError = planExpired || closestVolumeExpired;

  return (
    <div className="search-area">
      <form onSubmit={handleSearchSubmit} className="search-form">
        <div className="form-row">
          <div {...getRootProps({ className: `dropzone ${isError ? 'dropzone-error' : ''}` })}>
            <input {...getInputProps()} />
            <p className="dropzone-text">
              <FontAwesomeIcon icon={faUpload} className="upload-icon" />
              Glissez ou sélectionnez l'image
            </p>
          </div>
          <input 
            type="text" 
            value={text} 
            onChange={handleSearchTextChange} 
            placeholder="Description de l'objet" 
            className={`search-input ${isError ? 'input-error' : ''}`} 
            disabled={isError}
          />
          <button type="submit" className="search-submit-button" disabled={isError}>
            <FontAwesomeIcon icon={faSearch} />
          </button>
        </div>
      </form>
      <div className={`error-message-search ${isError ? 'show' : ''}`}>
        {planExpired && (
          <div className="plan-expired-message">
            Your trial period has ended. Please <Link to="/subscribe">upgrade your plan</Link>.
          </div>
        )}
        {closestVolumeExpired && (
          <div className="query-expired-message">
            You reached the volume limit of possible queries allocated to your plan. Please <button className='button-error-plan' onClick={() => { handleMenuClick("my-offers")}}>upgrade your plan</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchForm;