import React from "react";
import '../../css/Product.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faClock, faBullseye, faUsers, faGavel, faSearch, faCheck } from '@fortawesome/free-solid-svg-icons';
import problematicImage from '../../assets/landing_background.jpg'; 

const Product = () => {
    return (
        <div className="product-container">
            <h1>Artificial Intelligence is Necessary for Art Experts</h1>
            <p>
                Artificial intelligence helps art experts gain time, improve accuracy, and focus more on value-added work such as connecting with collectors, building auctions, and much more.
            </p>
            <div className="problematic-area">
                <div className="problematic-image">
                    <img src={problematicImage} alt="Problematic the startup is solving" />
                </div>
                <div className="problematic-text">
                    <h2>Search a Large Database of Past Sales, Houses, or Artists</h2>
                    <div className="pain-solution-container">
                        <div className="pain-points">
                            <div className="pain">
                                <FontAwesomeIcon icon={faSearch} />
                                <p>Time-consuming searches</p>
                            </div>
                            <div className="pain">
                                <FontAwesomeIcon icon={faBullseye} />
                                <p>Lack of accuracy</p>
                            </div>
                            <div className="pain">
                                <FontAwesomeIcon icon={faUsers} />
                                <p>Connecting with collectors</p>
                            </div>
                            <div className="pain">
                                <FontAwesomeIcon icon={faGavel} />
                                <p>Building auctions</p>
                            </div>
                        </div>
                        <div className="solutions">
                            <div className="solution">
                                <FontAwesomeIcon icon={faCheck} />
                                <p>Automated and fast search processes</p>
                            </div>
                            <div className="solution">
                                <FontAwesomeIcon icon={faCheck} />
                                <p>Highly accurate data and analytics</p>
                            </div>
                            <div className="solution">
                                <FontAwesomeIcon icon={faCheck} />
                                <p>Efficiently connect with collectors</p>
                            </div>
                            <div className="solution">
                                <FontAwesomeIcon icon={faCheck} />
                                <p>Streamlined auction creation</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Product;