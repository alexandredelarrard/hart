import React from "react";
import Header from "./Header.js";
import founder1 from "../../assets/avatar.png"; // Placeholder for founder 1 image
import founder2 from "../../assets/avatar.png"; // Placeholder for founder 2 image
import '../../css/About.css';

const About = ({t}) => {
    return (
        <div>
        <Header scrolled={true} t={t}/>
        <div className="about-container">
            <h1>About Artycs</h1>
            <section className="about-aim">
                <h2>Our Aim</h2>
                <p>
                    Leverage the very large number of past sales, auctions and external data to help art actors to better estimate, track and value art goods.
                    Our DNA is very much analytical since we would like to help the art world to be more accessible to the public, more transparent for buyers
                    and sellers, and overall make the sale process more fluid.
                </p>
                <p>
                    Our goal is also to fight against fake art pieces, fraudulent signatures which our AI tool will soon be able to help with.
                </p>
            </section>
            <section className="about-team">
                <h2>Our Team</h2>
                <div className="team-member">
                    <img src={founder1} alt="Founder 1" />
                    <h3>Founder 1 Name</h3>
                    <p>Brief description of founder 1, their background, and role in the company.</p>
                </div>
                <div className="team-member">
                    <img src={founder2} alt="Founder 2" />
                    <h3>Founder 2 Name</h3>
                    <p>Brief description of founder 2, their background, and role in the company.</p>
                </div>
            </section>
            <section className="about-backers">
                <h2>Our Backers</h2>
                <p>
                    Our backers include art experts from art auction houses and 2 commissaires priseurs who are driving our approach on a day-to-day basis to
                    fine-tune our value proposition as much as possible.
                </p>
            </section>
        </div>
    </div>
    );
}

export default About;
