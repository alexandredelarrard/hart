import React from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faClock, faBullseye, faUsers, faGavel, faSearch, faCheck } from '@fortawesome/free-solid-svg-icons';
import search_example from '../../assets/search_example_v2.jpg';
import estimate_example from '../../assets/price_example_v2.jpg';
import organize_example from '../../assets/organize_example_v2.jpg';

import '../../css/Product.css';

const Product = ({t}) => {

    const problematics = [

        {
            title: t("landing_page.product.titlesearch"),
            id:"product_2",
            image: search_example,
            painPoints: [
                { icon: faSearch, text: t("landing_page.product.pain1search")},
                { icon: faClock, text: t("landing_page.product.pain2search")},
                { icon: faUsers, text: t("landing_page.product.pain3search") },
                { icon: faGavel, text: t("landing_page.product.pain4search") }
            ],
            solutions: [
                { icon: faBullseye, text: t("landing_page.product.sol1search"), isBubble: true, number: "300 k"},
                { icon: faBullseye, text: t("landing_page.product.sol2search"), isBubble: true, number: "10 M"},
                { icon: faBullseye, text: t("landing_page.product.sol3search"), isBubble: true, number: "120"},
                { icon: faBullseye, text: t("landing_page.product.sol4search"), isBubble: true, number: "30 ans"}
            ]
        },
        {
            title: t("landing_page.product.titleautomatiestim"),
            description: t("landing_page.product.descautomatiestim"),
            id: "product_1",
            image: estimate_example,
            painPoints: [
                { icon: faClock, text: t("landing_page.product.pain1automatiestim") },
                { icon: faClock, text: t("landing_page.product.pain2automatiestim") },
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
            title: t("landing_page.product.titleoptim"),
            description: t("landing_page.product.descoptim"),
            id:"product_3",
            image: organize_example,
            painPoints: [
                { icon: faClock, text: t("landing_page.product.pain1optim") },
                { icon: faClock, text: t("landing_page.product.pain2optim") },
                { icon: faUsers, text: t("landing_page.product.pain3optim") },
                { icon: faGavel, text: t("landing_page.product.pain4optim") }
            ],
            solutions: [
                { icon: faCheck, text: t("landing_page.product.sol1optim") },
                { icon: faCheck, text: t("landing_page.product.sol2optim") },
                { icon: faCheck, text: t("landing_page.product.sol3optim") },
                { icon: faCheck, text: t("landing_page.product.sol4optim") }
            ]
        }
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
                            {/* <VideoComponent videoSrc={myVideo} /> */}
                            <img src={problem.image} alt="Firm Logo" />
                        </div>
                        <div className="problematic-text">
                            <h2>{problem.title}</h2>
                            <p>{problem.description}</p>
                            <div className="pain-solution-container">
                                <div className="solutions">
                                    {problem.solutions.map((solution, i) => (
                                        <div className="solution" key={i}>
                                            {solution.isBubble ? (
                                                <div className="bubble">{solution.number}</div>
                                            ) : (
                                                <FontAwesomeIcon icon={solution.icon} className="faicon green" />
                                            )}
                                            <p>{solution.text}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                    {index < problematics.length - 1 && <hr className="delimiter" />}
                </React.Fragment>
            ))}
            <hr className="delimiter" />
        </div>
    );
}

export default Product;
