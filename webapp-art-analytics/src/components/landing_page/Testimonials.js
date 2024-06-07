import React from "react";

const Testimonials = () => {
    return (
        <section className="testimonials-section">
            <h2>Testimonials</h2>
            <div className="testimonials-slider">
                <div className="testimonial">
                <img src="path-to-avatar1.jpg" alt="User Avatar" />
                <p>"This service transformed my auction experience!" - User A</p>
                </div>
                <div className="testimonial">
                <img src="path-to-avatar2.jpg" alt="User Avatar" />
                <p>"Incredible accuracy in art piece estimations." - User B</p>
                </div>
                <div className="testimonial">
                <img src="path-to-avatar3.jpg" alt="User Avatar" />
                <p>"A must-have for any art collector." - User C</p>
                </div>
            </div>
        </section>
        );
}
export default Testimonials;


