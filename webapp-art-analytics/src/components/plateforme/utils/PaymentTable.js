import React, { useMemo } from 'react';
import { AgGridReact } from 'ag-grid-react'; // React Data Grid Component

import "ag-grid-community/styles/ag-grid.css"; // Mandatory CSS required by the grid
import "ag-grid-community/styles/ag-theme-quartz.css"; // Optional Theme applied to the grid
import '../../../css/PaymentTable.css';

const PaymentTable = ({ payments, t }) => {

  // Exclude the user_id column and prepare column definitions
  const columns = useMemo(() => {
    return Object.keys(payments[0])
      .filter(key => key !== 'user_id')
      .map(key => ({
        headerName: key.replace(/_/g, ' '),
        field: key,
        sortable: true,
        filter: true,
        resizable: true,
        cellClassRules: {
          'rag-red': params => params.value <=0,
      }
      }));
  }, [payments]);

  if (!payments || payments.length === 0) {
    return <div>{t("plateforme.paymenttable.nopaymentavailable")}</div>;
  }

  return (
    <div className="ag-theme-quartz" style={{ height: 400}}>
      <AgGridReact
        rowData={payments}
        domLayout='autoHeight'
        columnDefs={columns}
        defaultColDef={{
          sortable: true,
          filter: true,
          resizable: true,
        }}
        pagination={true}
        paginationPageSize={10}
        // rowClassRules={rowClassRules}
      />
    </div>
  );
};

export default PaymentTable;