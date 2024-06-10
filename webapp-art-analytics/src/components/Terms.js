import React from 'react';
import HeaderWhite from "./landing_page/Header_white.js";
import { COMPANY_NAME } from "../utils/constants";
import { Link } from 'react-router-dom';
import '../css/Terms.css';

const Terms = () => {
  return (
    <div>
      <HeaderWhite/>
        <div className="terms-container">
            <h1>Conditions Générales d'Utilisation</h1>

            <h2>1. Introduction</h2>
            <p>
                Les présentes Conditions Générales d'Utilisation (ci-après "CGU") régissent l'accès et l'utilisation de la
                plateforme d'analyse d'art (ci-après "la Plateforme"). En utilisant la Plateforme, vous acceptez d'être lié par ces
                CGU.
            </p>

            <h2>2. Propriété Intellectuelle</h2>
            <p>
                Tous les contenus disponibles sur la Plateforme, y compris mais sans s'y limiter, les textes, images, graphismes,
                logos, icônes, et logiciels, sont protégés par des droits de propriété intellectuelle et sont la propriété exclusive
                de {COMPANY_NAME} ou de ses concédants. Toute reproduction, distribution, modification ou utilisation de ces
                contenus sans autorisation préalable écrite de {COMPANY_NAME} est strictement interdite.
            </p>

            <h2>3. Protection des Données Personnelles (GDPR)</h2>
            <p>
                En utilisant la Plateforme, vous consentez à la collecte et au traitement de vos données personnelles conformément
                au Règlement Général sur la Protection des Données (RGPD). Nous nous engageons à protéger votre vie privée et à
                garantir la sécurité de vos données personnelles.
            </p>

            <h3>3.1 Données Collectées</h3>
            <p>
                Nous collectons les informations suivantes :
                <ul>
                <li>Données d'identification (nom, adresse email, etc.)</li>
                <li>Données de connexion (adresse IP, type de navigateur, etc.)</li>
                <li>Données de navigation sur la Plateforme</li>
                </ul>
            </p>

            <h3>3.2 Utilisation des Données</h3>
            <p>
                Les données collectées sont utilisées pour :
                <ul>
                    <li>Fournir et améliorer nos services</li>
                    <li>Personnaliser votre expérience utilisateur</li>
                    <li>Répondre à vos demandes et vous contacter</li>
                    <li>Respecter nos obligations légales</li>
                </ul>
            </p>

            <h3>3.3 Droits de l'Utilisateur</h3>
            <p>
                Conformément à la réglementation en vigueur, vous disposez des droits suivants sur vos données personnelles :
                <ul>
                    <li>Droit d'accès</li>
                    <li>Droit de rectification</li>
                    <li>Droit à l'effacement</li>
                    <li>Droit à la limitation du traitement</li>
                    <li>Droit à la portabilité des données</li>
                    <li>Droit d'opposition</li>
                </ul>
                Pour exercer vos droits, veuillez <Link to="/contact">nous contacter</Link>.
            </p>

            <h2>4. Utilisation de la Plateforme</h2>
            <p>
                Vous vous engagez à utiliser la Plateforme conformément aux lois et règlements en vigueur, ainsi qu'aux présentes
                CGU. Il est interdit d'utiliser la Plateforme à des fins illicites, nuisibles ou frauduleuses.
            </p>

            <h2>5. Responsabilité</h2>
            <p>
            {COMPANY_NAME} s'efforce de fournir des informations précises et à jour sur la Plateforme, mais ne peut
                garantir l'exactitude, l'exhaustivité ou l'actualité des informations fournies. {COMPANY_NAME} ne saurait être
                tenue responsable des dommages directs ou indirects résultant de l'utilisation de la Plateforme.
            </p>

            <h2>6. Modifications des CGU</h2>
            <p>
            {COMPANY_NAME} se réserve le droit de modifier les présentes CGU à tout moment. Les modifications entreront
                en vigueur dès leur publication sur la Plateforme. Il vous appartient de consulter régulièrement les CGU pour prendre
                connaissance des éventuelles modifications.
            </p>

            <h2>7. Droit Applicable et Juridiction Compétente</h2>
            <p>
                Les présentes CGU sont régies par le droit français. Tout litige relatif à l'interprétation ou à l'exécution des
                présentes CGU sera soumis à la compétence exclusive des tribunaux français.
            </p>

            <h2>8. Contact</h2>
            <p>
                Pour toute question concernant les présentes CGU, vous pouvez <Link to="/contact">nous contacter</Link>.
            </p>

        </div>
    </div>
  );
};

export default Terms;