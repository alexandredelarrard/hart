import React from "react";
import { Link } from 'react-router-dom';
import { COMPANY_NAME } from "../utils/constants";
import logo from '../assets/logo_fond_blanc.jpg';
import '../css/Trial.css';

const Trial = () => {
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
                <h2>Testez Artycs gratuitement pendant 7 jours</h2>
                <form className="trial-form">
                    <div className="form-group">
                        <label>Prénom</label>
                        <input type="text" required />
                    </div>
                    <div className="form-group">
                        <label>Nom</label>
                        <input type="text" required />
                    </div>
                    <div className="form-group">
                        <label>Email professionnel</label>
                        <input type="email" required />
                    </div>
                    <div className="form-group">
                        <label>Mot de passe (8 caractères minimum)</label>
                        <input type="password" required />
                    </div>
                    <div className="form-group">
                        <label>Métier</label>
                        <select required>
                            <option value="">Sélectionnez...</option>
                            <option value="collector">Collector</option>
                            <option value="dealer">Dealer</option>
                            <option value="curator">Curator</option>
                            <option value="artist">Artist</option>
                        </select>
                    </div>
                    <div className="form-group">

                        <label>
                            <input type="checkbox" required /> 
                            J'accepte les <Link to="/terms">conditions générales d'utilisation</Link> et les <Link to="/terms">conditions générales de vente</Link>.
                        </label>
                    </div>
                    <button type="submit" className="trial-button">Commencer mon essai gratuit</button>
                </form>
                <hr className="login-delimiter" />
                <div className='login-trial'>
                    <p>Déjà inscrit ? <Link to="/login">connectez-vous à votre compte</Link>.</p>
                </div>
            </section>
        </div>
    );
}

export default Trial;