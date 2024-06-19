import React, { useState } from "react";
import Header from "./Header.js";
import '../../css/ContactUs.css';

const ContactUs = ({t}) => {
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
        <Header scrolled={true} t={t}/>
        <section className="contact-us-container">
            <h2>{t("overall.contactus")}</h2>
            <form className="contact-us-form" onSubmit={handleSubmit}>
                <div className="form-group">
                    <label>{t("overall.name")}</label>
                    <input type="text" name="name" value={formData.name} onChange={handleChange} required />
                </div>
                <div className="form-group">
                    <label>{t("overall.email")}</label>
                    <input type="email" name="email" value={formData.email} onChange={handleChange} required />
                </div>
                <div className="form-group">
                    <label>{t("landing_page.contactus.subject")}</label>
                    <input type="text" name="subject" value={formData.subject} onChange={handleChange} required />
                </div>
                <div className="form-group">
                    <label>{t("landing_page.contactus.message")}</label>
                    <textarea name="message" value={formData.message} onChange={handleChange} required></textarea>
                </div>
                <button type="submit" className="contact-us-button">{t("landing_page.contactus.sendmessage")}</button>
            </form>
        </section>
    </div>
    );
};

export default ContactUs;