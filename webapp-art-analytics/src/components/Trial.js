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
                            <option value="dealer">Expert</option>
                            <option value="curator">Commissaire priseur</option>
                            <option value="artist">Assurance & Finance</option>
                            <option value="collector">Particulier</option>
                            <option value="artist">Etudiant</option>
                        </select>
                    </div>
                    <div className="form-group checkbox-group">
                        <label>
                            <p>Nous collectons l’ensemble de ces informations pour vous créer un compte et ainsi permettre d’essayer les services proposés. Pour en savoir plus et connaître vos droits (accès, rectification, effacement, opposition, etc.), vous pouvez lire les conditions générales d'utilisation. La soumission du formulaire d’inscription sera considérée comme valant consentement de votre part à l’utilisation des informations vous concernant.</p>
                            <div className="checkbox-container">
                                <input type="checkbox" required />
                                <span>
                                    J'accepte les <Link to="/terms">conditions générales d'utilisation</Link> et les <Link to="/cgv">conditions générales de vente</Link>.
                                </span>
                            </div>
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