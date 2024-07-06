import React from "react";
import '../../css/Product.css';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faClock, faBullseye, faUsers, faGavel, faSearch, faCheck } from '@fortawesome/free-solid-svg-icons';
import problematicImage from '../../assets/landing_background_3.jpg';
import VideoComponent from './utils/VideoComponent';
import myVideo from '../../assets/Enregistrement 2024-06-22_intro1.mp4';

const Product = ({t}) => {

    const problematics = [
        {
            title: t("landing_page.product.titleautomatiestim"),
            description: t("landing_page.product.descautomatiestim"),
            id: "product_1",
            painPoints: [
                { icon: faClock, text: t("landing_page.product.pain1automatiestim") },
                { icon: faBullseye, text: t("landing_page.product.pain2automatiestim") },
                { icon: faUsers, text: t("landing_page.product.pain3automatiestim") },
                { icon: faGavel, text: t("landing_page.product.pain4automatiestim") }
            ],
            solutions: [
                { icon: faCheck, text: t("landing_page.product.sol1automatiestim") },
                { icon: faCheck, text: t("landing_page.product.sol2automatiestim") },
                { icon: faCheck, text: t("landing_page.product.sol3automatiestim") },
                { icon: faCheck, text: t("landing_page.product.sol4automatiestim") }
            ]
        },
        {
            title: t("landing_page.product.titlesearch"),
            description: t("landing_page.product.descsearch"),
            id:"product_2",
            painPoints: [
                { icon: faSearch, text: t("landing_page.product.pain1search")},
                { icon: faBullseye, text: t("landing_page.product.pain2search")},
                { icon: faUsers, text: t("landing_page.product.pain3search") },
                { icon: faGavel, text: t("landing_page.product.pain4search") }
            ],
            solutions: [
                { icon: faCheck, text: t("landing_page.product.sol1search")},
                { icon: faCheck, text: t("landing_page.product.sol2search")},
                { icon: faCheck, text: t("landing_page.product.sol3search")},
                { icon: faCheck, text: t("landing_page.product.sol4search")}
            ]
        },
        {
            title: t("landing_page.product.titleoptim"),
            description: t("landing_page.product.descoptim"),
            id:"product_3",
            painPoints: [
                { icon: faClock, text: t("landing_page.product.pain1optim") },
                { icon: faBullseye, text: t("landing_page.product.pain2optim") },
                { icon: faUsers, text: t("landing_page.product.pain3optim") },
                { icon: faGavel, text: t("landing_page.product.pain4optim") }
            ],
            solutions: [
                { icon: faCheck, text: t("landing_page.product.sol1optim") },
                { icon: faCheck, text: t("landing_page.product.sol2optim") },
                { icon: faCheck, text: t("landing_page.product.sol3optim") },
                { icon: faCheck, text: t("landing_page.product.sol4optim") }
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

    return (

        <div className="product-container">
            <h1 id="product">{t("landing_page.product.supertitle")}</h1>
            <p>
            {t("landing_page.product.superdesc")}
            </p>
            <hr className="delimiter" />
            {problematics.map((problem, index) => (
                <React.Fragment key={index}>
                    <div className={`problematic-area ${index % 2 === 1 ? "reverse" : t("landing_page.product.titleautomatiestim")}`} id={problem.id}>
                        <div className="problematic-image">
                            <VideoComponent videoSrc={myVideo} />
                            {/* <img src={problematicImage} alt="Problematic the startup is solving" /> */}
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
                            <div className="contentainer-firm-presentation-button">
                                <Link to="/login">
                                    <button className="firm-presentation-cta-button">{t("landing_page.product.buttonknowmore")}</button>
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
