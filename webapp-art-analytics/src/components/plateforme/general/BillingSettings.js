import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, Brush } from 'recharts';

import PaymentTable from "./PaymentTable.js";
import useFetchPayments from '../../../hooks/plateforme/useFetchPayments.js';
import useFetchMyActivity from '../../../hooks/plateforme/useFetchMyActivity.js';

import '../../../css/BillingSettings.css';

function BillingSettings({ t }) {
    const [payments, setPayments] = useState([]);
    const [activityData, setActivityData] = useState([]);

    useFetchPayments(setPayments);
    useFetchMyActivity(setActivityData);

    return (
      <div className="my-payment-section">
        <h2>{t("plateforme.profilesettings.myactivitytitle")}</h2>
        <div className="summary-area">
          <div className="left-chart">
            <BarChart
              className='settings-barchart'
              width={800}
              height={400}
              data={activityData}
              margin={{
                top: 20, right: 30, left: 20, bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="searchVolume" stackId="a" fill="#dc3545" />
              <Bar dataKey="estimateVolume" stackId="a" fill="#1964b3" />
              <Brush dataKey="date" height={40} stroke="#154d89" />
            </BarChart>
          </div>
            <div className="recap-container">
                <div className="middle">
                    <div className="part-header common-title">
                    <h2>{t("plateforme.profilesettings.monstatut")}</h2>
                    </div>
                    <div className="detail-container">
                        <p>Last subscription date: </p>
                        <p>Expiry date: </p>
                        <p>Subscription volume:</p>
                        <p>Remaining estimate volume</p>
                    </div>
                </div>
            </div>
        </div>
        <h2>{t("plateforme.profilesettings.billingtitle")}</h2>
        <div className="plans">
          <PaymentTable
            payments={payments}
            t={t}
          />
        </div>
      </div>
    );
  }

  export default BillingSettings;
