import React, {useState} from 'react';
import { useDropzone } from 'react-dropzone';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUpload, faSearch } from '@fortawesome/free-solid-svg-icons';

import "../../../css/SearchForm.css";

const SearchForm = ({
  text,
  onDrop,
  planExpired,
  closestVolumeExpired,
  handleSearchTextChange,
  handleSearchSubmit,
  handleMenuClick,
  t
}) => {

  const [selectedImage, setSelectedImage] = useState(null);

  const { getRootProps, getInputProps } = useDropzone({
    onDrop: (acceptedFiles) => {
      const file = acceptedFiles[0];
      setSelectedImage(URL.createObjectURL(file));
      onDrop(acceptedFiles);
    },
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
            {selectedImage ? (
              <img src={selectedImage} alt="Selected" className="dropzone-image-preview" />
            ) : (
              <p className="dropzone-text">
                <FontAwesomeIcon icon={faUpload} className="upload-icon" />
                {t("plateforme.search.dropzonedesc")}
              </p>
            )}
          </div>
          <input
            type="text"
            value={text || ''}
            onChange={handleSearchTextChange}
            placeholder={t("plateforme.search.textareadesc")}
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
            {t("plateforme.search.errorplanexpired")} <button className='button-error-plan' onClick={() => { handleMenuClick("my-offers")}}>{t("plateforme.search.upgradebutton")}</button>
          </div>
        )}
        {closestVolumeExpired && (
          <div className="query-expired-message">
            {t("plateforme.search.errorsearchclosevolume")} <button className='button-error-plan' onClick={() => { handleMenuClick("my-offers")}}>{t("plateforme.search.upgradebutton")}</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchForm;
