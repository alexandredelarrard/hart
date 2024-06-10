import React, { useState } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import Payment from "./landing_page/Payment.js";
import 'react-credit-cards-2/dist/es/styles-compiled.css';
import { Link } from 'react-router-dom';
import HeaderWhite from './landing_page/Header_white';
import '../css/Checkout.css';

const Checkout = () => {
  const [step, setStep] = useState(1);
  const [cardData, setCardData] = useState({
    number: '',
    name: '',
    expiry: '',
    cvc: '',
    focus: '',
  });
  const [userData, setUserData] = useState({
    email: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const handleUserChange = (e) => {
    const { name, value } = e.target;
    setUserData({ ...userData, [name]: value });
  };

  const handleCardChange = (e) => {
    const { name, value } = e.target;
    setCardData({ ...cardData, [name]: value });
  };

  const handleCardFocus = (e) => {
    setCardData({ ...cardData, focus: e.target.name });
  };

  const handleSignupOrSignin = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');

    try {
      const response = await axios.post('/api/auth', userData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      Cookies.set('token', response.data.token, { expires: 7 });
      setStep(2);
    } catch (error) {
      setError('Authentication failed. Please try again.');
    }
  };

  const handlePayment = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');

    const paymentData = {
      cardNumber: cardData.number,
      cardName: cardData.name,
      expiryDate: cardData.expiry,
      cvc: cardData.cvc,
      amount: Cookies.get('selectedPrice'),
    };

    try {
      const response = await axios.post('/api/payment', paymentData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      setMessage('Payment successful!');
      setStep(3);
    } catch (error) {
      setError('Payment failed. Please try again.');
    }
  };

  return (
    <div>
      <HeaderWhite />
      <div className="container-steps-indicator">
        <div className="steps-indicator">
            <div className={`step ${step === 1 ? 'active' : ''}`}>1. Identifiez-vous</div>
            <div className={`step ${step === 2 ? 'active' : ''}`}>2. Paiement</div>
            <div className={`step ${step === 3 ? 'active' : ''}`}>3. Confirmation</div>
        </div>
    </div>
      <div className="checkout-container">
        {step === 1 && (
          <div className="signup-signin-container">
            <h2>Sign Up or Sign In</h2>
            <form onSubmit={handleSignupOrSignin}>
              <div className="form-group">
                <label>Email:</label>
                <input
                  type="email"
                  name="email"
                  value={userData.email}
                  onChange={handleUserChange}
                  placeholder="Enter your email"
                  required
                />
              </div>
              <div className="form-group">
                <label>Password:</label>
                <input
                  type="password"
                  name="password"
                  value={userData.password}
                  onChange={handleUserChange}
                  placeholder="Enter your password"
                  required
                />
              </div>
              <button type="submit" className="checkout-button">Continue</button>
            </form>
            {error && <p className="error">{error}</p>}
          </div>
        )}
        {step === 2 && (
          <Payment
            cardData={cardData}
            handleSubmit={handlePayment}
            error={error}
            message={message}
            handleInputChange={handleCardChange}
            handleInputFocus={handleCardFocus}
          />
        )}
        {step === 3 && (
          <div className="confirmation-container">
            <h2>Payment Confirmation</h2>
            <p>Thank you for your purchase! Please check your email for confirmation.</p>
            <p>If you haven't received a confirmation email, please contact support.</p>
            <Link to="/contact" className="contact-link">Contact Support</Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default Checkout;