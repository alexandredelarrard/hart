import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import Payment from "./landing_page/Payment.js";
import 'react-credit-cards-2/dist/es/styles-compiled.css';
import { Link } from 'react-router-dom';
import {URL_API, URL_LOGIN} from '../utils/constants.js';
import HeaderWhite from './landing_page/Header_white.js';
import LoginElement from './connectors/LoginElement.js';
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

  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleCardChange = (e) => {
    const { name, value } = e.target;
    setCardData({ ...cardData, [name]: value });
  };

  const handleCardFocus = (e) => {
    setCardData({ ...cardData, focus: e.target.name });
  };

  useEffect(() => {
    const token = Cookies.get('token');
    if(token){
      const userdata = Cookies.get('userdata');
      const parsedUserdata = JSON.parse(userdata);
      setEmail(parsedUserdata.email);
      setStep(2);
    }
  }, []);

  const handleSubmit = async (e) => {
    setError(''); // Clear any previous error
    setMessage(''); // Clear any previous message
    e.preventDefault();
    try {
      const response = await axios.post(URL_API + URL_LOGIN, { email, password }, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      // Save token to localStorage and redirect to upload page
      Cookies.set('token', response.data.access_token, { expires: 0.5 });
      setStep(2)
    } catch (error) {
      if (error.response && error.response.status === 401) {
        setError('Invalid email or password');
      } else if (error.response && error.response.status === 404) {
        setError('Email not found');
      } else {
        setError('An error occurred. Please try again later.');
      }
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
      <div className="checkout-container">
        <div className="container-steps-indicator">
            <div className="steps-indicator">
                <div className={`step ${step === 1 ? 'active' : ''}`} onClick={() => setStep(1)}>1. Identifiez-vous</div>
                <div className={`step ${step === 2 ? 'active' : ''}`} onClick={() => step >1 && setStep(2)}>2. Paiement</div>
                <div className={`step ${step === 3 ? 'active' : ''}`} onClick={() => step >2 && setStep(3)}>3. Confirmation</div>
            </div>
        </div>
        {step === 1 && (
          <LoginElement
            handleSubmit={handleSubmit}
            email={email}
            password={password}
            error={error}
            message={message}
            setEmail={setEmail}
            setPassword={setPassword}
        />
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