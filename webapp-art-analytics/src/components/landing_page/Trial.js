import React, { useState } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import { Link } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import {URL_API, URL_SIGNIN, COMPANY_NAME} from '../../utils/constants';
import logo from '../../assets/logo_fond_blanc.jpg';
import '../../css/Trial.css';

const Trial = () => {
    const [email, setEmail] = useState('');
    const [emailError, setEmailError] = useState('');
    const [password, setPassword] = useState('');
    const [passwordError, setPasswordError] = useState('');
    const [username, setUsername] = useState('');
    const [surname, setSurname] = useState('');
    const [metier, setMetier] = useState('');
    const [otherJob, setOtherJob] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const validateEmail = (email) => {
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return emailRegex.test(email);
      };

    const validatePassword = (password) => {
        const regex = /^(?=.*[A-Z])(?=.*[^\w\s])(?=.{8,})/;
        return regex.test(password);
      };

    const handlePasswordChange = (e) => {
        const newPassword = e.target.value;
        setPassword(newPassword);
        if (!validatePassword(newPassword)) {
          setPasswordError('Le mdp doit contenir au moins 8 caractères, 1 majuscule et 1 caractère spécial.');
        } else {
          setPasswordError('');
        }
    };

    const handleEmailChange = (e) => {
        const newEmail = e.target.value;
        setEmail(newEmail);
        if (!validateEmail(newEmail)) {
          setEmailError("Veuillez entrer une adresse email valide.");
        } else {
          setEmailError('');
        }
      };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(''); // Clear any previous error
    
        const jobTitle = metier === 'other' ? otherJob : metier;
    
        try {
          const response = await axios.post(`${URL_API}${URL_SIGNIN}`, { 
            "surname": surname, 
            "username": username, 
            "email": email, 
            "password": password, 
            metier: jobTitle }, {
            headers: {
              'Content-Type': 'application/json',
            },
          });
    
          // Save token to cookies and redirect to analytics
          Cookies.set('token', response.data.access_token, { expires: 0.5 });
          Cookies.set('userdata', JSON.stringify(response.data.userdata), { expires: 0.5 });
          setMessage(response.data.message);
          navigate('/analytics');
        } catch (error) {
          if (error.response && error.response.status === 401) {
            setError('Invalid email or password');
          } else if (error.response && error.response.status === 404) {
            setError('Email already in use, please try to login');
          } else {
            setError('An error occurred. Please try again later.');
          }
        }
      };

    return (
        <div className="trial-container">
            <header className="navbar-scrolled">
                <div className="logo-container">
                    <a href="/" className="logo">
                        <img src={logo} alt="Firm Logo" className="firm-logo"/>
                    </a>
                    <span className="company-name">{COMPANY_NAME}</span>
                </div>
                <Link to="/login">
                    <button className="account-button">Mon compte</button>
                </Link>
            </header>
            <section className="trial-form-section">
                <h2>Testez gratuitement pendant 7 jours</h2>
                <form className="trial-form"  onSubmit={handleSubmit}>
                    <div className="form-row">
                        <div className="form-group">
                            <label>Prénom</label>
                            <input 
                                type="text" 
                                value={surname}
                                placeholder="Votre prenom"
                                onChange={(e) => setSurname(e.target.value)}
                                required 
                            />
                        </div>
                        <div className="form-group">
                            <label>Nom</label>
                            <input 
                                type="text" 
                                value={username}
                                placeholder="Votre nom"
                                onChange={(e) => setUsername(e.target.value)}
                                required 
                            />
                        </div>
                    </div>
                    <div className="form-group">
                        <label>Email professionnel</label>
                        <input 
                            type="email"
                            value={email}
                            onChange={handleEmailChange}
                            placeholder="Entrez votre email"
                            required
                        />
                        {emailError && <p style={{ color: 'red' }}>{emailError}</p>}
                    </div>
                    <div className="form-group">
                        <label>Mot de passe (8 caractères minimum, 1 majuscule et 1 caractère spécial)</label>
                        <input 
                            type="password"
                            value={password}
                            onChange={handlePasswordChange}
                            placeholder="Entrez votre Mot de passe"
                            required
                        />
                        {passwordError && <p style={{ color: 'red' }}>{passwordError}</p>}
                    </div>
                    <div className="form-group">
                        <label>Métier</label>
                        <select 
                            value={metier}
                            onChange={(e) => setMetier(e.target.value)}
                            required>
                                <option value="">Sélectionnez...</option>
                                <option value="independent">Particulier</option>
                                <option value="expert">Expert</option>
                                <option value="commissaire">Commissaire priseur</option>
                                <option value="insurance">Assureur</option>
                                <option value="student">Étudiant</option>
                                <option value="other">Autre</option>
                        </select>
                    </div>
                    {metier === 'other' && (
                    <div className="form-group">
                        <label>Autre Métier</label>
                        <input
                            type="text"
                            value={otherJob}
                            placeholder="Précisez votre métier"
                            onChange={(e) => setOtherJob(e.target.value)}
                            required
                        />
                    </div>
                    )}
                    <div className="form-group checkbox-group">
                        <label>
                            <p>Nous collectons l’ensemble de ces informations pour vous créer un compte puis ajuster les fonctionnalités pour vous proposer les meilleurs services. Pour en savoir plus et connaître vos droits (accès, rectification, effacement, opposition, etc.), vous pouvez lire les conditions générales d'utilisation. La soumission du formulaire d’inscription sera considérée comme valant consentement de votre part à l’utilisation des informations collectées.</p>
                            <div className="checkbox-container">
                                <input type="checkbox" required />
                                <span>
                                    J'accepte les <Link to="/terms">conditions générales d'utilisation</Link> et les <Link to="/cgv">conditions générales de vente</Link>.
                                </span>
                            </div>
                        </label>
                    </div>
                    <button type="submit" className="trial-button" disabled={passwordError || emailError}>Commencer mon essai gratuit</button>
                </form>
                {message && <p className="message">{message}</p>}
                {error && <p className="error">{error}</p>}
                <hr className="login-delimiter" />
                <div className='login-trial'>
                    <p>Déjà inscrit ? <Link to="/login">connectez-vous à votre compte</Link>.</p>
                </div>
            </section>
        </div>
    );
}

export default Trial;