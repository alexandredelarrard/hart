import React from "react";
import '../../css/InfoBand.css'; 

const InfoBand = () => {
    return (
        
        <section className="background-section">
            <div className='info-band'>
                <h2>WE WANT YOU TO KNOW:</h2>
                <div className="info-items">
                    <div className="info-item">
                    <div className="icon">📦</div>
                    <div>
                        <h3>1. Delivering eCommerce expertise</h3>
                        <p>Since 2011, we've been gathering eCommerce expertise and delivering it to our clients</p>
                    </div>
                    </div>
                    <div className="info-item">
                    <div className="icon">📈</div>
                    <div>
                        <h3>2. Helping win a race</h3>
                        <p>Thanks to the expertise, the merchants leave their competitors behind and win the markets</p>
                    </div>
                    </div>
                    <div className="info-item">
                    <div className="icon">💲</div>
                    <div>
                        <h3>3. Making stores sell more</h3>
                        <p>By winning the markets, our clients boost their sales and revenue</p>
                    </div>
                    </div>
                </div>
            </div>
        </section>
    );
}

export default InfoBand;