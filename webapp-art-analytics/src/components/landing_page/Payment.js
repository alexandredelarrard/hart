import React  from 'react';
import Cards from 'react-credit-cards-2';
import Cookies from 'js-cookie';

import 'react-credit-cards-2/dist/es/styles-compiled.css';
import '../../css/Payment.css';

function Payment({cardData, 
  handleSubmit, 
  error, 
  message, 
  handleInputChange, 
  handleInputFocus
}) {

  return (
    <div className="payment-container">
      {/* <div className="payment-summary">
        <h3>Summary</h3>
        <p>Selected Plan: {Cookies.get('selectedPlan')}</p>
        <p>Price: {Cookies.get('selectedPrice')} euros</p>
      </div> */}
      <div className="payment-form-container">
        <h2>Payment Details</h2>
        <Cards
          number={cardData.number}
          name={cardData.name}
          expiry={cardData.expiry}
          cvc={cardData.cvc}
          focused={cardData.focus}
        />
        <form onSubmit={handleSubmit} className="payment-form">
          <div className="form-group">
            <label>Card Number:</label>
            <input
              type="tel"
              name="number"
              value={cardData.number}
              onChange={handleInputChange}
              onFocus={handleInputFocus}
              placeholder="Enter your card number"
              required
            />
          </div>
          <div className="form-group">
            <label>Name on Card:</label>
            <input
              type="text"
              name="name"
              value={cardData.name}
              onChange={handleInputChange}
              onFocus={handleInputFocus}
              placeholder="Enter name on card"
              required
            />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Expiry Date:</label>
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
          <button type="submit" className="payment-button">Pay Now</button>
        </form>
        {message && <p className="message">{message}</p>}
        {error && <p className="error">{error}</p>}
      </div>
    </div>
  );
};

export default Payment;