import React from "react";

const Pricing = () => {
    return (
        <div>
           <section className="pricing-section">
                <h2>Pricing</h2>
                <div className="pricing-container">
                    <div className="pricing-card">
                    <h3 className="pricing-title">Discover</h3>
                    <ul className="pricing-features">
                        <li>✔️ Auction results</li>
                        <li>✔️ Upcoming auctions</li>
                        <li>✔️ Unlimited Searches</li>
                        <li>✔️ Artwork images and artist signatures</li>
                    </ul>
                    <div className="pricing-options">
                        <p>€35</p>
                        <p>1 day</p>
                        <p>Get your money back</p>
                    </div>
                    <div className="pricing-options">
                        <p>€231.20 <span className="old-price">€289</span></p>
                        <p>1 year + 92 days</p>
                    </div>
                    <button className="subscribe-button">Subscribe</button>
                    </div>
                    <div className="pricing-card">
                    <h3 className="pricing-title">Advanced</h3>
                    <ul className="pricing-features">
                        <li>✔️ Auction results</li>
                        <li>✔️ Upcoming auctions</li>
                        <li>✔️ Unlimited Searches</li>
                        <li>✔️ Artwork images and artist signatures</li>
                        <li>✔️ Artist Analytics</li>
                        <li>✔️ Artprice Indicators®</li>
                        <li>✔️ Custom lot lists</li>
                    </ul>
                    <div className="pricing-options">
                        <p>€51</p>
                        <p>per monthly subscription</p>
                    </div>
                    <div className="pricing-options">
                        <p>€351.20 <span className="old-price">€439</span></p>
                        <p>1 year + 92 days</p>
                    </div>
                    <button className="subscribe-button">Subscribe</button>
                    </div>
                    <div className="pricing-card">
                    <h3 className="pricing-title">Professional</h3>
                    <ul className="pricing-features">
                        <li>✔️ Auction results</li>
                        <li>✔️ Upcoming auctions</li>
                        <li>✔️ Unlimited Searches</li>
                        <li>✔️ Artwork images and artist signatures</li>
                        <li>✔️ Artist Analytics</li>
                        <li>✔️ Artprice Indicators®</li>
                        <li>✔️ Custom lot lists</li>
                        <li>✔️ Artprice Store</li>
                    </ul>
                    <div className="pricing-options">
                        <p>€61</p>
                        <p>per monthly subscription</p>
                    </div>
                    <div className="pricing-options">
                        <p>€484 <span className="old-price">€605</span></p>
                        <p>1 year + 92 days</p>
                    </div>
                    <button className="subscribe-button">Subscribe</button>
                    </div>
                </div>
                </section>
        </div>
        );
}
export default Pricing;



