import React from 'react';
import '../../../css/PaymentTable.css';

const PaymentTable = ({payments}) => {

    if (!payments || payments.length === 0) {
        return <div>No payment data available</div>;
      }
      
    // Exclude the user_id column
    const columns = Object.keys(payments[0]).filter(key => key !== 'user_id');
  
    return (
      <div className="table-container">
        <table className="payment-table">
          <thead>
            <tr>
              {columns.map((col, index) => (
                <th key={index} style={{ fontWeight: 'bold' }}>{col.replace(/_/g, ' ')}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {payments.map((payment, index) => (
              <tr key={index}>
                {columns.map((col, index) => (
                  <td key={index}>{payment[col]}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };
  
  export default PaymentTable;