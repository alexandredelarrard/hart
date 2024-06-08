import React from "react";
import '../../css/Product.css';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faClock, faBullseye, faUsers, faGavel, faSearch, faCheck, faArrowRight } from '@fortawesome/free-solid-svg-icons';
import problematicImage from '../../assets/landing_background_3.jpg'; 

const problematics = [
    {
        title: "Recherchez intelligemment vos oeuvres dans plus de 10 millions d'articles",
        description: "L'IA vous permet de rechercher en comparant l'image ou le texte de votre oeuvre avec celles de notre base de référence en cherchant une oeuvre, un artiste ou une vente.",
        painPoints: [
            { icon: faSearch, text: "Recherche limitée par mots clés"},
            { icon: faBullseye, text: "Recherche itérative lente"},
            { icon: faUsers, text: "Aucune analyse de tendance" },
            { icon: faGavel, text: "Données limités" }
        ],
        solutions: [
            { icon: faCheck, text: "Recherche par l'image et/ou le texte"},
            { icon: faCheck, text: "Affinage par nos critères fins"},
            { icon: faCheck, text: "Analyses de tendances, de CA de l'artiste et plus encore"},
            { icon: faCheck, text: "Données mises à jour toutes les 24h"}
        ]
    },
    {
        title: "Estimez automatiquement vos oeuvres",
        description: "A partir d'une simple photo et sans connaissance de l'oeuvre, vous pouvez désormais observer toutes les ventes passées similaires. Vous pouvez contextualiser votre image par le texte pour ajuster l'estimation.",
        painPoints: [
            { icon: faClock, text: "Estimation manuelle" },
            { icon: faBullseye, text: "Aucune désigantion" },
            { icon: faUsers, text: "Prix des oeuvres similaires non contextualisable" },
            { icon: faGavel, text: "Aucune historisation du travail" }
        ],
        solutions: [
            { icon: faCheck, text: "Estimation automatique avec intervalle de confiance" },
            { icon: faCheck, text: "Désignation automatique par IA générative (ChatGpt)" },
            { icon: faCheck, text: "Simulateur de prix par géolocalisation, date, etc." },
            { icon: faCheck, text: "Mémorisation de vos estimations dans le temps" }
        ]
    },
    {
        title: "Optimize Art Market Analysis",
        description: "Use AI to gain insights into art market trends and pricing strategies.",
        painPoints: [
            { icon: faClock, text: "Outdated market data" },
            { icon: faBullseye, text: "Inconsistent pricing" },
            { icon: faUsers, text: "Identifying market trends" },
            { icon: faGavel, text: "Evaluating art pieces" }
        ],
        solutions: [
            { icon: faCheck, text: "Up-to-date market data" },
            { icon: faCheck, text: "Consistent pricing analysis" },
            { icon: faCheck, text: "Accurate market trend identification" },
            { icon: faCheck, text: "Comprehensive art evaluation" }
        ]
    },
    {
        title: "Streamline Auction Preparations",
        description: "AI helps streamline the preparation and execution of art auctions.",
        painPoints: [
            { icon: faClock, text: "Time-consuming preparation" },
            { icon: faBullseye, text: "Coordination challenges" },
            { icon: faUsers, text: "Reaching potential buyers" },
            { icon: faGavel, text: "Managing bids" }
        ],
        solutions: [
            { icon: faCheck, text: "Efficient auction preparation" },
            { icon: faCheck, text: "Seamless coordination" },
            { icon: faCheck, text: "Effective buyer outreach" },
            { icon: faCheck, text: "Streamlined bid management" }
        ]
    }
];

const Product = () => {
    return (
        <div className="product-container" id="product">
            <h1>Découvrez l'avenir de l'expertise artistique avec des solutions IA sur mesure, pour vous.</h1>
            <p>
                Le marché de l'art est décentralisé. Les outils traditionnels ne suffisent plus. Seule l'intelligence artificielle vous permet de contextualiser rapidement une œuvre, de la comparer aux ventes récentes mondiales, d'interpréter son évaluation puis d'optimiser votre vente.
            </p>
            <hr className="delimiter" />
            {problematics.map((problem, index) => (
                <React.Fragment key={index}>
                    <div className={`problematic-area ${index % 2 === 1 ? "reverse" : ""}`}>
                        <div className="problematic-image">
                            <img src={problematicImage} alt="Problematic the startup is solving" />
                        </div>
                        <div className="problematic-text">
                            <h2>{problem.title}</h2>
                            <p>{problem.description}</p>
                            <div className="pain-solution-container">
                                <div className="pain-points">
                                    {problem.painPoints.map((pain, i) => (
                                        <div className="pain" key={i}>
                                            <FontAwesomeIcon icon={pain.icon} className="faicon" />
                                            <p>{pain.text}</p>
                                        </div>
                                    ))}
                                </div>
                                <div className="solutions">
                                    {problem.solutions.map((solution, i) => (
                                        <div className="solution" key={i}>
                                            <FontAwesomeIcon icon={solution.icon} className="faicon green" />
                                            <p>{solution.text}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                            <div className="contentainer-product-button">
                                <Link to="/login">
                                    <button className="product-cta-button">En savoir plus ... </button>
                                </Link>
                            </div>
                        </div>
                    </div>
                    {index < problematics.length - 1 && <hr className="delimiter" />}
                </React.Fragment>
            ))}
        </div>
    );
}

export default Product;