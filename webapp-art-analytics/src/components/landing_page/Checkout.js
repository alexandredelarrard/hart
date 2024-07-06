import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import { Link } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';

import Header from './Header.js';
import Payment from "./Payment.js";
import {login, checkAuth} from "../../hooks/general/identification.js";
import LoginElement from '../connectors/LoginElement.js';

import 'react-credit-cards-2/dist/es/styles-compiled.css';
import '../../css/Checkout.css';

const Checkout = ({t}) => {
  const navigate = useNavigate();
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
    const checkUserAuth = async () => {
      const isAuthenticated = await checkAuth();
      if (isAuthenticated){
        const userdata = Cookies.get('userdata');
        if(userdata){
          const parsedUserdata = JSON.parse(userdata);
          setEmail(parsedUserdata.email);
          setStep(2);
        }
      } else {
        navigate('/login');
      }
    };

    checkUserAuth()
  }, [setStep, setEmail, navigate]);

  const handleSubmit = async (e) => {
    setError('');
    setMessage('');
    e.preventDefault();

    try {

      const response = await login(email, password);
      setMessage(response.data.message);
      setStep(2);

    } catch (error) {
      if (error.response && error.response.status === 401) {
        setError(t("landing_page.trial.error401"));
      } else if (error.response && error.response.status === 404) {
        setError(t("landing_page.trial.erroremailnotfound"));
      } else {
        setError(t("landing_page.trial.errorglobal"));
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
      setMessage(t("landing_page.checkout.messagegoodpauyment"));
      setStep(3);
    } catch (error) {
      setError(t("landing_page.checkout.messagebadpauyment"));
    }
  };

  return (
    <div>
      <Header scrolled={true} t={t}/>
      <div className="checkout-container">
        <div className="container-steps-indicator">
            <div className="steps-indicator">
                <div className={`step ${step === 1 ? 'active' : ''}`} onClick={() => setStep(1)}>{t("landing_page.checkout.menu1title")}</div>
                <div className={`step ${step === 2 ? 'active' : ''}`} onClick={() => step >1 && setStep(2)}>{t("landing_page.checkout.menu2title")}</div>
                <div className={`step ${step === 3 ? 'active' : ''}`} onClick={() => step >2 && setStep(3)}>{t("landing_page.checkout.menu3title")}</div>
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
            t={t}
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
            t={t}
          />
        )}
        {step === 3 && (
          <div className="confirmation-container">
            <h2>{t("landing_page.checkout.confirmationtitle")}</h2>
            <p>{t("landing_page.checkout.confirmationdesc1")}</p>
            <p>{t("landing_page.checkout.confirmationdesc2")}</p>
            <Link to="/contact" className="contact-link">{t("overall.contactus")}</Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default Checkout;
