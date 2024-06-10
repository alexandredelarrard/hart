import React from "react";
import image1 from '../../assets/logo.jpg';
import image2 from '../../assets/logo.jpg';
import image3 from '../../assets/avatar.png';
import image4 from '../../assets/logo.jpg';

import "../../css/Advantages.css";

const advantagesData = [
    {
        image: image1,
        points: [
            "It saves time",
            "It enables to find a good price and not sell too cheap or too expensive",
            "It reduces the number of unsold elements"
        ]
    },
    {
        image: image2,
        points: [
            "It increase accuracy",
            "It enables to find a good price and not sell too cheap or too expensive",
            "It reduces the number of unsold elements"
        ]
    },
    {
        image: image3,
        points: [
            "It increase overall turnover",
            "It enables to find a good price and not sell too cheap or too expensive",
            "It reduces the number of unsold elements"
        ]
    },
    {
        image: image4,
        points: [
            "It reduces remaining sales",
            "It enables to find a good price and not sell too cheap or too expensive",
            "It reduces the number of unsold elements"
        ]
    }
];

const Advantages = () => {
    return (
        <div className="advantages-background-container">
            <div className="advantages-container">
                <h2>Des bénéfices tangibles mesurés auprès des utilisateurs</h2>
                {advantagesData.map((advantage, index) => (
                    <div className="advantage-row" key={index}>
                        <div className="advantage-image">
                            <img src={advantage.image} alt={`Advantage ${index + 1}`} />
                        </div>
                        <div className="advantage-text">
                            <ul>
                                {advantage.points.map((point, i) => (
                                    <li key={i}>{point}</li>
                                ))}
                            </ul>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default Advantages;



