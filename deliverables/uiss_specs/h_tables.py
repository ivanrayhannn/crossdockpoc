"""Table structures of the replicated G-TOPAS tables (from the I/F layouts H01-25 DVJO820, H02-02 DVJO250, H02-53 DVJO950).
Column: [name, type, PK, Null, description]. Physical names follow the table exports (TB_R_H0202_DEMAND_HISTORY_SUM, TB_R_H0253_ORDER_CONTROL_PRE, TB_M_H0125_DESTINATION)."""

H0125_COLS = [
[
"DESTINATION_CD",
"VARCHAR(7)",
"Y",
"N",
"Used by Crossdock (destination list, upload check, DEST_CODE). No.1 Destination Code"
],
[
"CUSTOMER_CD",
"VARCHAR(7)",
"",
"N",
"No.2 Customer Code"
],
[
"DOMESTIC_OVERSEA_CLASS_CD",
"VARCHAR(1)",
"",
"N",
"No.3 Domestic/Overseas Classification Code: '1': Domestic, '2': Overseas"
],
[
"ORDER_TRANSPORTATION_CD",
"VARCHAR(1)",
"",
"N",
"No.4 Order Transportation Code: 1':AIR '2':SEA '3':LAND"
],
[
"BO_INSTRUCTION_CD",
"VARCHAR(1)",
"",
"N",
"No.5 B/O Instruction Code: 'K': B/O Cancel, 'F': Follow-up, 'M': Follow-up(S/O only)"
],
[
"TARIFF_CD_INPUT_REQUIRED_FLAG",
"VARCHAR(1)",
"",
"N",
"No.6 Tariff Code Input Required Flag: '0':Not check '1':check"
],
[
"QUP_PROCESS_CD",
"VARCHAR(1)",
"",
"N",
"No.7 QUP Process Code: '1':Round-up '2':Not change '3':Round-down"
],
[
"DEPOT_DEST_JUDGMENT_FLAG",
"VARCHAR(1)",
"",
"N",
"No.8 Depot Destination Judgment Flag: \"0\":Not Depot \"1\":Depot"
],
[
"REGION_CD",
"VARCHAR(2)",
"",
"N",
"No.9 Region Code"
],
[
"REGION_NAME",
"VARCHAR(50)",
"",
"Y",
"No.10 Region Name"
],
[
"DESTINATION_GROUPING_CD",
"VARCHAR(7)",
"",
"N",
"No.11 Destination Grouping Code"
],
[
"FREIGHT_AGENT_CD_AIR",
"VARCHAR(3)",
"",
"N",
"No.12 Freight Agent Code (Air)"
],
[
"FREIGHT_AGENT_CD_SEA",
"VARCHAR(3)",
"",
"N",
"No.13 Freight Agent Code (Sea)"
],
[
"FREIGHT_AGENT_CD_LAND",
"VARCHAR(3)",
"",
"N",
"No.14 Freight Agent Code (Land)"
],
[
"PACKING_TYPE_CD",
"VARCHAR(2)",
"",
"N",
"No.15 Packing Type Code: '1': 40 feet (FCL) '2': 20 feet (FCL) '3': LCL"
],
[
"DESTINATION_OPERATOR_CD",
"VARCHAR(2)",
"",
"Y",
"No.16 Destination Operator Code"
],
[
"DESTINATION_OPERATOR_NAME",
"VARCHAR(20)",
"",
"Y",
"No.17 Destination Operator Name"
],
[
"DESTINATION_NAME_ENG",
"VARCHAR(50)",
"",
"N",
"Used by Crossdock (shown with the code). No.18 Destination Name"
],
[
"DESTINATION_NAME_LOCAL",
"VARCHAR(75)",
"",
"Y",
"No.19 Destination Name (Local Language)"
],
[
"COUNTRY_NAME_ENG",
"VARCHAR(36)",
"",
"Y",
"No.20 Country Name"
],
[
"COUNTRY_NAME_LOCAL",
"VARCHAR(54)",
"",
"Y",
"No.21 Country Name (Local Language)"
],
[
"POSTAL_CD_ENG",
"VARCHAR(10)",
"",
"Y",
"No.22 Postal Code"
],
[
"POSTAL_CD_LOCAL",
"VARCHAR(15)",
"",
"Y",
"No.23 Postal Code (Local Language)"
],
[
"STATE_CD_ENG",
"VARCHAR(6)",
"",
"Y",
"No.24 State Code"
],
[
"STATE_CD_LOCAL",
"VARCHAR(9)",
"",
"Y",
"No.25 State Code (Local Language)"
],
[
"DESTINATION_ADDR1_ENG",
"VARCHAR(50)",
"",
"N",
"No.26 Destination Address1"
],
[
"DESTINATION_ADDR2_ENG",
"VARCHAR(50)",
"",
"Y",
"No.27 Destination Address2"
],
[
"DESTINATION_ADDR1_LOCAL",
"VARCHAR(75)",
"",
"Y",
"No.28 Destination Address1(Local Language)"
],
[
"DESTINATION_ADDR2_LOCAL",
"VARCHAR(75)",
"",
"Y",
"No.29 Destination Address2(Local Language)"
],
[
"PHONE_NO",
"VARCHAR(20)",
"",
"Y",
"No.30 Phone No."
],
[
"FAX_NO",
"VARCHAR(20)",
"",
"Y",
"No.31 Fax No."
],
[
"REGISTRANT_ID",
"VARCHAR(13)",
"",
"Y",
"No.32 Registrant ID"
],
[
"UPDATE_JOB_ID",
"VARCHAR(8)",
"",
"Y",
"No.33 Update Job ID"
],
[
"UPDATE_OPERATOR_ID",
"VARCHAR(13)",
"",
"Y",
"No.34 Update Operator ID"
],
[
"INTF_UPDATE_DT",
"TIMESTAMP",
"",
"Y",
"No.35 Update Date & Time"
],
[
"CREATE_DT",
"TIMESTAMP",
"",
"Y",
"Created date and time (NSP)"
],
[
"CREATE_BY",
"VARCHAR(TBD)",
"",
"Y",
"Created by (NSP)"
],
[
"UPDATE_DT",
"TIMESTAMP",
"",
"Y",
"Updated date and time (NSP)"
],
[
"UPDATE_BY",
"VARCHAR(TBD)",
"",
"Y",
"Updated by (NSP)"
]
]

H0202_COLS = [
[
"CUSTOMER_CD",
"VARCHAR(7)",
"Y",
"N",
"No.1 Customer Code"
],
[
"CUSTOMER_ORDER_NO",
"VARCHAR(8)",
"Y",
"N",
"No.2 Customer Order No."
],
[
"ORDER_DT",
"DATE",
"Y",
"N",
"No.3 Order Date"
],
[
"ORDER_TIME",
"VARCHAR(6)",
"Y",
"N",
"No.4 Order Time"
],
[
"DESTINATION_CD",
"VARCHAR(7)",
"Y",
"N",
"No.5 Destination Code"
],
[
"DETAILED_ITEM_NO",
"VARCHAR(4)",
"Y",
"N",
"No.6 Detailed Item No."
],
[
"SERIAL_NO",
"VARCHAR(7)",
"Y",
"N",
"No.7 Serial No."
],
[
"DEMAND_HISTORY_UPDATE_CD",
"VARCHAR(2)",
"Y",
"N",
"No.8 Demand History Update Code: '01': Reject Records Update '02': Irregular Order P Cancel Update '03': Vendor Direct Shipment Update '05': Firm Order History Update '06': "
],
[
"DEPOT_CD",
"VARCHAR(2)",
"",
"Y",
"No.9 Depot Code"
],
[
"DOMESTIC_OVERSEAS_CLASS_CD",
"VARCHAR(1)",
"",
"Y",
"No.10 Domestic/Overseas Classification Code: '1': Domestic, '2': Overseas"
],
[
"REGION_CD",
"VARCHAR(2)",
"",
"Y",
"No.11 Region Code"
],
[
"ORDER_MAKER_CD",
"VARCHAR(1)",
"",
"Y",
"No.12 Order Maker Code"
],
[
"ORDER_PART_NO",
"VARCHAR(15)",
"",
"Y",
"No.13 Order P/No."
],
[
"SHIPPING_PART_NO",
"VARCHAR(15)",
"",
"Y",
"No.14 Shipping P/No."
],
[
"DEMAND_HISTORY_DT",
"DATE",
"",
"Y",
"No.15 Demand History Date"
],
[
"ORDER_TRANSPORTATION_CD",
"VARCHAR(1)",
"",
"Y",
"No.16 Order Transportation Code: '1': AIR, '2': SEA, '3': LAND"
],
[
"TOPAS_ORDER_TYPE",
"VARCHAR(1)",
"",
"Y",
"No.17 TOPAS Order Type: '1': VOR, '2': E/O, '3': S/O, 'F': F/O"
],
[
"SUPPLIER_CD",
"VARCHAR(5)",
"",
"Y",
"No.18 Supplier Code"
],
[
"CREATED_DEMAND_FLAG",
"VARCHAR(1)",
"",
"Y",
"No.19 Created Demand Flag: '0': No created demand, '1': Created demand"
],
[
"ORDER_ERROR_CD",
"VARCHAR(2)",
"",
"Y",
"No.20 Order Error Code"
],
[
"RA_CD",
"VARCHAR(2)",
"",
"Y",
"No.21 R/A Code"
],
[
"ORDER_PORTION_CD",
"VARCHAR(1)",
"",
"Y",
"No.22 Order Portion Code: '1': Reject '2': Alteration '3': Process '4': Amendment"
],
[
"ORDER_QTY_DEMAND_QTY",
"NUMBER(8)",
"",
"Y",
"No.23 Order Qty , Demand Qty"
],
[
"SHIPPING_QTY",
"NUMBER(8)",
"",
"Y",
"No.24 Original Shipping Qty or Estimated Shipping Qty"
],
[
"REJECT_QTY",
"NUMBER(8)",
"",
"Y",
"No.25 Reject Qty"
],
[
"ETC_CANCEL_QTY",
"NUMBER(8)",
"",
"Y",
"No.26 ETC Cancel Qty"
],
[
"DIRECT_DELIVERY_QTY",
"NUMBER(8)",
"",
"Y",
"No.27 Direct Delivery Qty"
],
[
"FIRM_ORDER_QTY",
"NUMBER(8)",
"",
"Y",
"No.28 Firm Order Qty"
],
[
"CROSS_DOCK_QTY",
"NUMBER(8)",
"",
"Y",
"No.29 Cross Dock Qty"
],
[
"PROCESS_QTY",
"NUMBER(8)",
"",
"Y",
"No.30 Process Qty"
],
[
"BO_CANCEL_QTY",
"NUMBER(8)",
"",
"Y",
"No.31 B/O Cancel Qty"
],
[
"NON_TARGET_ORDER_QTY_FLAG",
"VARCHAR(1)",
"",
"Y",
"No.32 Non-Target of Cumulative Order Qty Flag: '0':Target of cumulation (Regular or 1st division of large order division) '1': Non-target of cumulation (2nd or later divisions of large or"
],
[
"REGISTRANT_ID",
"VARCHAR(13)",
"",
"Y",
"No.33 Registrant ID"
],
[
"UPDATE_JOB_ID",
"VARCHAR(8)",
"",
"Y",
"No.34 Update Job ID"
],
[
"UPDATE_OPERATOR_ID",
"VARCHAR(13)",
"",
"Y",
"No.35 Update Operator ID"
],
[
"INTF_UPDATE_DT",
"TIMESTAMP",
"",
"Y",
"No.36 Update Date & Time"
],
[
"CREATE_DT",
"TIMESTAMP",
"",
"Y",
"Created date and time (NSP)"
],
[
"CREATE_BY",
"VARCHAR(TBD)",
"",
"Y",
"Created by (NSP)"
],
[
"UPDATE_DT",
"TIMESTAMP",
"",
"Y",
"Updated date and time (NSP)"
],
[
"UPDATE_BY",
"VARCHAR(TBD)",
"",
"Y",
"Updated by (NSP)"
]
]

H0253_COLS = [
[
"CUSTOMER_CD",
"VARCHAR(7)",
"Y",
"N",
"No.1 Customer Code"
],
[
"CUSTOMER_ORDER_NO",
"VARCHAR(8)",
"Y",
"N",
"No.2 Customer Order No."
],
[
"ORDER_DT",
"DATE",
"Y",
"N",
"No.3 Order Date"
],
[
"ORDER_TIME",
"VARCHAR(6)",
"Y",
"N",
"No.4 Order Time"
],
[
"DESTINATION_CD",
"VARCHAR(7)",
"Y",
"N",
"No.5 Destination Code"
],
[
"DETAILED_ITEM_NO",
"VARCHAR(4)",
"Y",
"N",
"No.6 Detailed Item No."
],
[
"SERIAL_NO",
"VARCHAR(7)",
"Y",
"N",
"TBD: in the I/F layout (unique key) but not in the table export - confirm. No.7 Serial No., Card No."
],
[
"TOPAS_ORDER_TYPE",
"VARCHAR(1)",
"",
"Y",
"No.8 TOPAS Order Type: '1': VOR, '2': E/O, '3': S/O, 'F': F/O"
],
[
"DEMAND_HISTORY_UPDATE_DT",
"DATE",
"",
"Y",
"No.9 Demand History Update Date"
],
[
"SHIPPING_MAKER_CD",
"VARCHAR(1)",
"",
"Y",
"No.10 Shipping Maker Code"
],
[
"SHIPPING_PART_NO",
"VARCHAR(15)",
"",
"Y",
"No.11 Shipping P/No."
],
[
"ORIGINAL_SHIPPING_QTY",
"NUMBER(8)",
"",
"Y",
"No.12 Original Shipping Qty or Estimated Shipping Qty"
],
[
"ORDER_STATUS_QTY",
"NUMBER(8)",
"",
"Y",
"No.13 Order Status Qty"
],
[
"ORDER_STATUS",
"VARCHAR(1)",
"",
"Y",
"No.14 Order Status: '1': Pending '2': Reject/Cancel '3': B/O '4': Firm Order '5': Vender Direct '6': Allocation '7': Cross Dock"
],
[
"BO_INSTRUCTION_CD",
"VARCHAR(1)",
"",
"Y",
"No.15 B/O Instruction Code: '1': B/O Cancel, '9': Follow-up"
],
[
"BO_RELEASE_DT",
"DATE",
"",
"Y",
"No.16 B/O Release Date"
],
[
"ORDER_GROUP",
"VARCHAR(2)",
"",
"Y",
"No.17 Order Group"
],
[
"DIRECT_DELIVERY_CD",
"VARCHAR(1)",
"",
"Y",
"No.18 Direct Delivery Code: Blank: Not vendor direct delivery '1': Vendor direct delivery"
],
[
"DIRECT_DELIVERY_FLAG",
"VARCHAR(1)",
"",
"Y",
"No.19 Direct Delivery Flag: '0': Not direct delivery, '1': Direct delivery"
],
[
"CURRENCY_CD",
"VARCHAR(3)",
"",
"Y",
"No.20 Currency Code"
],
[
"LANDED_COST",
"NUMBER(14,3)",
"",
"Y",
"No.21 Landed Cost: Constant '0'"
],
[
"NET_PRICE",
"NUMBER(14,3)",
"",
"Y",
"No.22 Nett Price"
],
[
"SALES_PRICE",
"NUMBER(14,3)",
"",
"Y",
"No.23 Sales Price"
],
[
"EXPORT_SALES_PRICE",
"NUMBER(14,3)",
"",
"Y",
"No.24 Export Sales Price"
],
[
"SPECIAL_PRICE_CD",
"VARCHAR(1)",
"",
"Y",
"No.25 Special Price Code: '1': Special price, Blank: Not applicable"
],
[
"ORDER_DISCOUNT_CD",
"VARCHAR(4)",
"",
"Y",
"No.26 Order Discount Code"
],
[
"ITEM_DISCOUNT_RATE",
"NUMBER(6,1)",
"",
"Y",
"No.27 Item Discount Rate"
],
[
"FIRST_ALLOCATION_DT",
"DATE",
"",
"Y",
"No.28 1st Allocation Date"
],
[
"BO_HISTORY_CD",
"VARCHAR(1)",
"",
"Y",
"No.29 B/O History Code: '0': Default, '1': B/O"
],
[
"ORDER_ERROR_CD",
"VARCHAR(2)",
"",
"Y",
"No.30 Order Error Code"
],
[
"RA_CD",
"VARCHAR(2)",
"",
"Y",
"No.31 R/A Code"
],
[
"PENDING_ORDER_CD",
"VARCHAR(2)",
"",
"Y",
"No.32 Pending Order Code"
],
[
"ORDER_PORTION_CD",
"VARCHAR(1)",
"",
"Y",
"No.33 Order Portion Code: '1': Reject '2': Alteration '3': Process '4': Amendment"
],
[
"ORDER_STATUS_DT",
"DATE",
"",
"Y",
"No.34 Order Status Date"
],
[
"SHIPPING_PROCESS_CTRL_CD",
"VARCHAR(1)",
"",
"Y",
"No.35 Shipping Process Control Code: Blank: No change '1': Higher priority to B/O"
],
[
"PROCUREMENT_PROCESS_CTRL_CD",
"VARCHAR(1)",
"",
"Y",
"No.36 Procurement Process Control Code: '1': Skip substitution check '2': Skip large order division (including skipping irregular order check) '3': '2' + skip order taking check '4"
],
[
"DANGEROUS_GOODS_CLASS",
"VARCHAR(4)",
"",
"Y",
"No.37 Dangerous Goods Class"
],
[
"CREATE_DEMAND_FLAG",
"VARCHAR(1)",
"",
"Y",
"No.38 Created Demand Flag: '0': Not created demand, '1': Created demand"
],
[
"SPECIAL_CUSTOMER_FLAG",
"VARCHAR(1)",
"",
"Y",
"No.39 Special Customer Flag: '0': Regular, '1': Special"
],
[
"POSS_TRANSMISSION_JUDG_FLAG",
"VARCHAR(1)",
"",
"Y",
"No.40 POSS Transmission Judgment Flag: '0': Out of target, '1': Transmission target"
],
[
"REGISTRANT_ID",
"VARCHAR(13)",
"",
"Y",
"No.41 Registrant ID"
],
[
"UPDATE_JOB_ID",
"VARCHAR(8)",
"",
"Y",
"No.42 Update Job ID"
],
[
"UPDATE_OPERATION_ID",
"VARCHAR(13)",
"",
"Y",
"No.43 Update Operator ID"
],
[
"INTF_UPDATE_DT",
"TIMESTAMP",
"",
"Y",
"No.44 Update Date & Time"
],
[
"CREATE_DT",
"TIMESTAMP",
"",
"Y",
"Created date and time (NSP)"
],
[
"CREATE_BY",
"VARCHAR(TBD)",
"",
"Y",
"Created by (NSP)"
],
[
"UPDATE_DT",
"TIMESTAMP",
"",
"Y",
"Updated date and time (NSP)"
],
[
"UPDATE_BY",
"VARCHAR(TBD)",
"",
"Y",
"Updated by (NSP)"
]
]
