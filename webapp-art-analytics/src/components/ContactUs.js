import React, { useState } from "react";
import HeaderWhite from "./landing_page/Header_white.js";
import '../css/ContactUs.css';

const ContactUs = () => {
    const [formData, setFormData] = useState({
        name: "",
        email: "",
        subject: "",
        message: ""
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        // Handle form submission logic here, such as sending the email
        console.log("Form data submitted:", formData);
    };

    return (
        <div>
        <HeaderWhite/>
        <section className="contact-us-container">
            <h2>Contact Us</h2>
            <form className="contact-us-form" onSubmit={handleSubmit}>
                <div className="form-group">
                    <label>Name</label>
                    <input type="text" name="name" value={formData.name} onChange={handleChange} required />
                </div>
                <div className="form-group">
                    <label>Email</label>
                    <input type="email" name="email" value={formData.email} onChange={handleChange} required />
                </div>
                <div className="form-group">
                    <label>Subject</label>
                    <input type="text" name="subject" value={formData.subject} onChange={handleChange} required />
                </div>
                <div className="form-group">
                    <label>Message</label>
                    <textarea name="message" value={formData.message} onChange={handleChange} required></textarea>
                </div>
                <button type="submit" className="contact-us-button">Send Message</button>
            </form>
        </section>
    </div>
    );
};

export default ContactUs;