import React, {useState} from 'react';
import PaymentTable from "./PaymentTable.js"
import useFetchPayments from '../../../hooks/plateforme/useFetchPayments.js';

function BillingSettings({t}) {

    const [payments, setPayments] = useState([]);   
    useFetchPayments(setPayments);

    return (
        <div className="my-payment-section">
        <h2>{t("plateforme.profilesettings.billingtitle")}</h2>
        <div className="plans">
            <div className="">
                <PaymentTable 
                    payments={payments}
                    t={t}
                />
            </div>
        </div>
        </div>
    );
}

export default BillingSettings;