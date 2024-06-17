import React, { useState, useEffect } from 'react';
import Cookies from 'js-cookie';
import '../../css/CookieConsent.css';

const CookieConsent = () => {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const consent = Cookies.get('cookieConsent');
    if (!consent) {
      setVisible(true);
    }
  }, []);

  const handleAccept = () => {
    Cookies.set('cookieConsent', 'accepted', { expires: 90 });
    setVisible(false);
  };

  const handleDecline = () => {
    Cookies.set('cookieConsent', 'declined', { expires: 90 });
    setVisible(false);
  };

  if (!visible) {
    return null;
  }

  return (
    <div className="cookie-consent-banner">
      <p>We use cookies to improve your experience on our site. By accepting, you agree to our use of cookies. <a href="/terms">Learn more</a></p>
      <button onClick={handleAccept}>Accept</button>
      <button onClick={handleDecline}>Decline</button>
    </div>
  );
};

export default CookieConsent;