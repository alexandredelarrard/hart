import React, { Fragment, useEffect } from "react";
import Cookies from 'js-cookie';
import FirmPresentation from "./landing_page/FirmPresentation.js";
import Header from "./landing_page/Header.js";
import Footer from "./landing_page/Footer.js";
import Pricing from "./landing_page/Pricing.js";
import Advantages from "./landing_page/Advantages.js";
import Product from "./landing_page/Product.js";
import InfoBand from "./landing_page/InfoBand.js";
import Testimonials from "./landing_page/Testimonials.js"
import CookieConsent from "./landing_page/CookieConsent";
import '../css/Home.css'; // Assuming you have a Home.css file for styling

const Home = () => {

  useEffect(() => {
    // Access geolocation
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((position) => {
        const { latitude, longitude } = position.coords;
        Cookies.set('geolocation', JSON.stringify({ latitude, longitude }), { expires: 7 });
        console.log(Cookies.get("geolocation"))
      }, (error) => {
        console.error("Error accessing geolocation: ", error);
      });
    }

    // Access machine specifications
    const machineSpecs = {
      userAgent: navigator.userAgent,
      platform: navigator.platform,
      language: navigator.language,
      screenResolution: `${window.screen.width}x${window.screen.height}`
    };
    Cookies.set('machineSpecs', JSON.stringify(machineSpecs), { expires: 7 });

  }, []);

  return (
    <Fragment>

      <Header />
                
      <FirmPresentation />

      <InfoBand/>
      
      <Product/>

      <Advantages/>

      <Pricing
        isplateforme={false}
      />

      {/* <Testimonials/> */}

      <Footer/>

      <CookieConsent />

    </Fragment>
  );
};

export default Home;