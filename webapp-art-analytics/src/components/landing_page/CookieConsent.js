import React, { useState, useEffect } from 'react';
import Cookies from 'js-cookie';
import '../../css/CookieConsent.css';

const CookieConsent = ({t}) => {
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
      <p>{t("landing_page.cookiesconsent.desc")} <a href="/terms">{t("landing_page.cookiesconsent.learnmore")}</a></p>
      <button onClick={handleAccept}>{t("landing_page.cookiesconsent.buttonaccept")}</button>
      <button onClick={handleDecline}>{t("landing_page.cookiesconsent.buttondecline")}</button>
    </div>
  );
};

export default CookieConsent;