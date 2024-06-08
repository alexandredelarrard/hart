import React, {Fragment} from "react";
import FirmPresentation from "./landing_page/FirmPresentation.js";
import Header from "./landing_page/Header.js";
import Footer from "./landing_page/Footer.js";
import Pricing from "./landing_page/Pricing.js";
import Advantages from "./landing_page/Advantages.js";
import Product from "./landing_page/Product.js";
import InfoBand from "./landing_page/InfoBand.js";
import Testimonials from "./landing_page/Testimonials.js"
import '../css/Home.css'; // Assuming you have a Home.css file for styling

const Home = () => {
  return (
    <Fragment>

      <Header />
                
      <FirmPresentation />

      <InfoBand/>
      
      <Product/>

      <Advantages/>

      <Pricing/>

      {/* <Testimonials/> */}

      <Footer/>

    </Fragment>
  );
};

export default Home;