import React, { useState } from "react";
import Header from "./Header.js";
import axiosInstance_middle from '../../hooks/general/axiosInstance';
import { URL_CONTACT_US } from "../../utils/constants";
import {validateEmail} from '../../utils/general.js';
import '../../css/ContactUs.css';

const ContactUs = ({changeLanguage, t}) => {
    const [formData, setFormData] = useState({
        name: "",
        email: "",
        subject: "",
        message: ""
    });

    const [responseMessage, setResponseMessage] = useState("");

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axiosInstance_middle.post(URL_CONTACT_US, {
                'email_content': formData
            },{
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (response.status === 200) {
                setResponseMessage("Email data saved successfully!");
            } else {
                setResponseMessage("Failed to save email data. Please try again.");
            }
        } catch (error) {
            console.error("Error saving email data:", error);
            setResponseMessage("An error occurred. Please try again later.");
        }
    };

    return (
        <div>
        <Header changeLanguage={changeLanguage} scrolled={true} t={t}/>
        <section className="contact-us-container">
            <h2>{t("overall.contactus")}</h2>
            {!responseMessage && (
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
            </form>)}
            {responseMessage &&
                <div className="quote">{responseMessage}</div>
            }
        </section>
    </div>
    );
};

export default ContactUs;
