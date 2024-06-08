import React from "react";
import avatar from "../../assets/avatar.png";
import "../../css/Testimonials.css"


const testimonials = [
    { text: "This service transformed my auction experience!", user: "User A" },
    { text: "Incredible accuracy in art piece estimations.", user: "User B" },
    { text: "A must-have for any art collector.", user: "User C" },
    { text: "Efficient and accurate!", user: "User D" },
    { text: "Highly recommended for serious collectors.", user: "User E" }
];

const Testimonials = () => {
    return (
        <section className="testimonials-section">
            <h2>Testimonials</h2>
            <div className="testimonials-slider">
                {testimonials.map((testimonial, index) => (
                    <div className="testimonial" key={index}>
                        <img src={avatar} alt="User Avatar" />
                        <p>"{testimonial.text}" - {testimonial.user}</p>
                    </div>
                ))}
            </div>
        </section>
    );
}

export default Testimonials;

