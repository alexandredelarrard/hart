import React from "react";
import '../../css/Product.css';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faClock, faBullseye, faUsers, faGavel, faSearch, faCheck, faArrowRight } from '@fortawesome/free-solid-svg-icons';
import problematicImage from '../../assets/landing_background_3.jpg'; 

const problematics = [
    {
        title: "Estimez automatiquement vos oeuvres",
        description: "Recherchez en soumettant une simple image ou un descriptif pointu, l'IA se charge de vous trouver les pièces correspondantes et les prix associés.",
        id:"product_2",
        painPoints: [
            { icon: faClock, text: "Aucune estimation claire" },
            { icon: faBullseye, text: "Estimation longue par recherche manuelle" },
            { icon: faUsers, text: "Aucune explication sur les prix passés" },
            { icon: faGavel, text: "Aucune espace de travail personnalisé" }
        ],
        solutions: [
            { icon: faCheck, text: "Estimation automatique précise et interprétable" },
            { icon: faCheck, text: "Estimation en quelques secondes" },
            { icon: faCheck, text: "Prix passés expliqués par géolocalisation, date, etc." },
            { icon: faCheck, text: "Espace de travail dédié, historisé" }
        ]
    },
    {
        title: "Recherchez intelligemment vos oeuvres dans plus de 10 millions d'articles",
        description: "Recherchez toutes les oeuvre d'un artiste, ou toute oeuvre dans le même jus que la votre à partir de critères très fins.",
        id:"product_1",
        painPoints: [
            { icon: faSearch, text: "Recherche limitée par mots clés"},
            { icon: faBullseye, text: "Recherche itérative lente"},
            { icon: faUsers, text: "Aucune analyse de tendance" },
            { icon: faGavel, text: "Données limités" }
        ],
        solutions: [
            { icon: faCheck, text: "Recherche par l'image et/ou le texte"},
            { icon: faCheck, text: "Recherche par critères fins, materiau, dimension, etc."},
            { icon: faCheck, text: "Analyses de tendances, de CA de l'artiste et plus encore"},
            { icon: faCheck, text: "Données mises à jour toutes les 24h"}
        ]
    },
    {
        title: "Maximisez le CA de votre vente",
        description: "Grâce à notre moteur d'optimisation, vous pouvez désormais optimiser l'organisation de vos lots au sein de la vente afin vendre au mieux chaque lot tout en minimisant le nombre de lots non vendus.",
        id:"product_3",
        painPoints: [
            { icon: faClock, text: "Répartition des lots manuelle" },
            { icon: faBullseye, text: "Volume de lots non vendus non négligeable" },
            { icon: faUsers, text: "Vue limitée du potentiel de votre vente" },
            { icon: faGavel, text: "Pas d'outil de suivi de vos ventes" }
        ],
        solutions: [
            { icon: faCheck, text: "Outil d'organisation de vente pour maximiser votre CA" },
            { icon: faCheck, text: "Minimisation du nombre de lots non vendus" },
            { icon: faCheck, text: "Estimation statistique de ce que votre vente donnerait" },
            { icon: faCheck, text: "Ajustement de l'optimiseur à partir du résultat de vos ventes passées" }
        ]
    },
    // {
    //     title: "Authentification de vos oeuvres",
    //     description: "Afin d'éviter toute vente de contrefaçon et vous aider à les identifier, nous avons développé un outil de comparaison de signatures, sceaux, poinçons ou signe distinctif d'authentification.",
    //     id:"product_4",
    //     painPoints: [
    //         { icon: faClock, text: "Authentification complexe, sous évaluant l'oeuvre" },
    //         { icon: faBullseye, text: "Expertise difficile à construire" },
    //         { icon: faUsers, text: "Ressources limitées d'identification" },
    //         { icon: faGavel, text: "Au cas par cas" }
    //     ],
    //     solutions: [
    //         { icon: faCheck, text: "Authentification semi automatisée" },
    //         { icon: faCheck, text: "Données visuelles pour +10 000 signes (marque, signature, etc.)" },
    //         { icon: faCheck, text: "Données internationales centralisées, tout type d'objet" },
    //         { icon: faCheck, text: "Premières analyses en quelques secondes" }
    //     ]
    // }
];

const Product = () => {
    return (
        <div className="product-container" id="product">
            <h1>Une plateforme pour extraire le potentiel des données, de l'art et de l'IA</h1>
            <p>
                Le marché de l'art est décentralisé. Les outils traditionnels ne suffisent plus. Seule l'intelligence artificielle vous permet de contextualiser rapidement une œuvre, de la comparer aux ventes récentes mondiales, d'interpréter son évaluation puis d'optimiser votre vente.
            </p>
            <hr className="delimiter" />
            {problematics.map((problem, index) => (
                <React.Fragment key={index}>
                    <div className={`problematic-area ${index % 2 === 1 ? "reverse" : ""}`} id={problem.id}>
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