import React  from 'react';
import Cards from 'react-credit-cards-2';

import 'react-credit-cards-2/dist/es/styles-compiled.css';
import '../../css/Payment.css';

function Payment({cardData,
  handleSubmit,
  error,
  message,
  handleInputChange,
  handleInputFocus,
  t
}) {

  return (
    <div className="payment-container">
      <div className="payment-form-container">
        <h2>{t("landing_page.payment.title")}</h2>
        <Cards
          number={cardData.number}
          name={cardData.name}
          expiry={cardData.expiry}
          cvc={cardData.cvc}
          focused={cardData.focus}
        />
        <form onSubmit={handleSubmit} className="payment-form">
          <div className="form-group">
            <label>{t("landing_page.payment.cardnumbertitle")}:</label>
            <input
              type="tel"
              name="number"
              value={cardData.number}
              onChange={handleInputChange}
              onFocus={handleInputFocus}
              placeholder={t("landing_page.payment.cardnumberdesc")}
              required
            />
          </div>
          <div className="form-group">
            <label>{t("landing_page.payment.cardownertitle")}:</label>
            <input
              type="text"
              name="name"
              value={cardData.name}
              onChange={handleInputChange}
              onFocus={handleInputFocus}
              placeholder={t("landing_page.payment.cardownerdesc")}
              required
            />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>{t("landing_page.payment.expirydatetitle")}:</label>
              <input
                type="tel"
                name="expiry"
                value={cardData.expiry}
                onChange={handleInputChange}
                onFocus={handleInputFocus}
                placeholder="MM/YY"
                required
              />
            </div>
            <div className="form-group">
              <label>CVC:</label>
              <input
                type="tel"
                name="cvc"
                value={cardData.cvc}
                onChange={handleInputChange}
                onFocus={handleInputFocus}
                placeholder="CVC"
                required
              />
            </div>
          </div>
          <button type="submit" className="login-button">{t("landing_page.payment.paynow")}</button>
        </form>
        {message && <p className="message">{message}</p>}
        {error && <p className="error">{error}</p>}
      </div>
    </div>
  );
};

export default Payment;
