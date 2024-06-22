import React, { useMemo } from 'react';
import { AgGridReact } from 'ag-grid-react'; // React Data Grid Component

import "ag-grid-community/styles/ag-grid.css"; // Mandatory CSS required by the grid
import "ag-grid-community/styles/ag-theme-quartz.css"; // Optional Theme applied to the grid
import '../../../css/PaymentTable.css';

const PaymentTable = ({ payments, t }) => {

  const paymentsWithId = payments.map((payment, index) => ({ ...payment, id: index + 1 }));

  // Exclude the user_id column and prepare column definitions
  const columns = useMemo(() => {
    if (payments.length !== 0) {
      return [
        { 
          headerName: 'ID', 
          field: 'id', 
          sortable: false, 
          filter: false, 
          resizable: false, 
          width: 50 
        },
        ...Object.keys(payments[0])
          .filter(key => key !== 'user_id')
          .map(key => ({
            headerName: key.replace(/_/g, ' '),
            field: key,
            sortable: true,
            filter: true,
            resizable: true,
            width: 150, // Fixed column width
            cellClassRules: {
              'rag-red': params => params.value <= 0,
            }
          }))
      ];
    }
    return [];
  }, [payments]);

  if (!payments || payments.length === 0) {
    return <div>{t("plateforme.paymenttable.nopaymentavailable")}</div>;
  }

  return (
    <div className="payment-table ag-theme-quartz">
       <AgGridReact
        rowData={paymentsWithId}
        domLayout='autoHeight'
        columnDefs={columns}
        defaultColDef={{
          sortable: true,
          filter: true,
          resizable: true,
        }}
        pagination={true}
        paginationPageSize={10}
      />
    </div>
  );
};

export default PaymentTable;