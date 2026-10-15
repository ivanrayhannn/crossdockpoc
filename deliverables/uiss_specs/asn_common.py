"""Shared definitions for the ASN Crossdock documents (X8 creation screen, X12 instruction batch, X13 inquiry screen)."""

NAME, PROJ = 'FID Rayhan', 'Crossdock Optimization'
NC = 'Not changed'
INSTR, ASNH, ASND, DRAFT = '#TB_R_INSTRUCTION', 'TB_R_ASN_CROSSDOCK_H', 'TB_R_ASN_CROSSDOCK_D', '#TEMP_ASN_DRAFT'
H0253, PRA_M, PRA_P = 'TB_R_H0253_ORDER_CONTROL_PRE', 'TB_R_PRA_DAILY_ORDER_MANIFEST', 'TB_R_PRA_DAILY_ORDER_PART'
DM = 'TB_M_H0125_DESTINATION'

INSTR_COLS = [
    ["INSTRUCTION_ID", "BIGINT", "Y", "N", "Running number within the session"],
    ["CUSTOMER_CD", "VARCHAR(7)", "", "N", "H0253.CUSTOMER_CD"],
    ["CUSTOMER_ORDER_NO", "VARCHAR(8)", "", "N", "H0253.CUSTOMER_ORDER_NO"],
    ["ORDER_DT", "DATE", "", "N", "Customer Order Date (H0253.ORDER_DT)"],
    ["DESTINATION_CD", "VARCHAR(7)", "", "N", "H0253.DESTINATION_CD (TB_M_H0125_DESTINATION)"],
    ["DETAILED_ITEM_NO", "VARCHAR(4)", "", "N", "H0253.DETAILED_ITEM_NO"],
    ["SERIAL_NO", "VARCHAR(7)", "", "N", "H0253.SERIAL_NO"],
    ["PART_NO", "VARCHAR(15)", "", "N", "Order part number (H0253.SHIPPING_PART_NO)"],
    ["ORDER_STATUS", "VARCHAR(1)", "", "N", "H0253.ORDER_STATUS ('7' Cross Dock)"],
    ["CUST_ORDER_QTY", "NUMBER(8)", "", "N", "Order status qty of the customer order line (H0253.ORDER_STATUS_QTY)"],
    ["ASSIGNED_QTY", "NUMBER(8)", "", "N", "Qty of the line pre-mapped to this PO (0 for the not-assigned row)"],
    ["REMAINING_ORDER_QTY", "NUMBER(8)", "", "N", "Qty of the line still without a PO after this assignment"],
    ["PO_NO", "VARCHAR(TBD)", "", "Y", "Supplier PO number (Pra Daily Order Manifest); NULL while not assigned"],
    ["MANIFEST_NO", "VARCHAR(TBD)", "", "Y", "Manifest number"],
    ["MANIFEST_ITEM_NO", "VARCHAR(TBD)", "", "Y", "Manifest item number (Pra Daily Order Part)"],
    ["PO_ORDER_DT", "DATE", "", "Y", "Order date of the PO (PO Date)"],
    ["PO_ORDER_QTY", "NUMBER(TBD)", "", "Y", "Order qty of the PO part"],
    ["SUPPLIER_CD", "VARCHAR(TBD)", "", "Y", "Supplier code"],
    ["SUPPLIER_PLANT", "VARCHAR(TBD)", "", "Y", "Supplier plant"],
    ["SUB_SUPPLIER_CD", "VARCHAR(TBD)", "", "Y", "Sub supplier code"],
    ["SUB_SUPPLIER_PLANT", "VARCHAR(TBD)", "", "Y", "Sub supplier plant"],
    ["ORDER_TYPE", "VARCHAR(TBD)", "", "Y", "Order type of the PO"],
    ["DOCK_CD", "VARCHAR(TBD)", "", "Y", "Dock code"],
    ["ETD_ORI", "DATE", "", "Y", "Original ETD"],
    ["CROSSDOCK_STATUS", "VARCHAR(1)", "", "N", "Status of the unit (Part Number + Customer Order Date): '6' Ready / '7' Not Ready"]]
INSTR_TABLE = {"name": INSTR, "kind": "temp", "proposed": True,
               "description": "Temporary table of one Get Order run (session): customer order line (H0253, order status 7, Hold Flag N, not mapped) "
                              "pre-mapped to a supplier PO (Pra Daily Order), FIFO by order date. One row per line x PO, plus one row with PO_NO NULL "
                              "for the qty still without a PO. Columns proposed.",
               "columns": INSTR_COLS}

DRAFT_COLS = [
    ["CASE_SEQ", "NUMBER(4)", "Y", "N", "Case sequence in the draft (Case 1, 2, ...)"],
    ["LINE_SEQ", "NUMBER(4)", "Y", "N", "Order line x PO within the case"],
    ["PART_NO", "VARCHAR(15)", "", "N", "Part number of the case"],
    ["ORDER_DT", "DATE", "", "N", "Customer Order Date of the case"],
    ["DESTINATION_CD", "VARCHAR(7)", "", "N", "Destination of the case"],
    ["CUSTOMER_CD", "VARCHAR(7)", "", "N", "Customer code"],
    ["CUSTOMER_ORDER_NO", "VARCHAR(8)", "", "N", "Customer order number"],
    ["DETAILED_ITEM_NO", "VARCHAR(4)", "", "N", "Detailed item number"],
    ["SERIAL_NO", "VARCHAR(7)", "", "N", "Serial number"],
    ["QTY", "NUMBER(8)", "", "N", "Qty of the line in the case (mapped to the PO)"],
    ["PO_NO", "VARCHAR(TBD)", "", "N", "PO number"],
    ["MANIFEST_NO", "VARCHAR(TBD)", "", "N", "Manifest number"],
    ["MANIFEST_ITEM_NO", "VARCHAR(TBD)", "", "N", "Manifest item number"],
    ["PO_ORDER_QTY", "NUMBER(TBD)", "", "N", "PO qty"],
    ["DELIVERY_DT", "DATE", "", "N", "Delivery Date of the Get Order"],
    ["RIT_CYCLE", "VARCHAR(TBD)", "", "N", "Rit of the Get Order"],
    ["ROUTE", "VARCHAR(TBD)", "", "N", "Route of the Rit"]]
DRAFT_TABLE = {"name": DRAFT, "kind": "temp", "proposed": True,
               "description": "Temporary ASN draft built by [Create ASN] (mapping of the selected units); read by the Case List and by [Submit ASN]. Columns proposed.",
               "columns": DRAFT_COLS}

ASNH_COLS = [
    ["ASN_NO", "VARCHAR(TBD)", "Y", "N", "ASN number (existing numbering)"],
    ["SUPPLIER_CD", "VARCHAR(TBD)", "", "N", "Supplier of the cases"],
    ["SUPPLIER_PLANT", "VARCHAR(TBD)", "", "N", "Supplier plant"],
    ["DELIVERY_DT", "DATE", "", "N", "Delivery Date"],
    ["RIT_CYCLE", "VARCHAR(TBD)", "", "N", "Rit"],
    ["ROUTE", "VARCHAR(TBD)", "", "N", "Route of the Rit"],
    ["TOTAL_CASE", "NUMBER", "", "N", "Number of cases"],
    ["TOTAL_QTY", "NUMBER", "", "N", "Delivery Qty (total pieces)"],
    ["ASN_STATUS", "VARCHAR(1)", "", "N", "'1' Created (set on submit)"],
    ["CREATED_BY", "VARCHAR(TBD)", "", "N", "User who submitted the ASN"],
    ["CREATED_DT", "DATETIME", "", "N", "Submit date and time"],
    ["CHANGED_BY", "VARCHAR(TBD)", "", "N", "User who last changed the record"],
    ["CHANGED_DT", "DATETIME", "", "N", "Last changed date and time"]]
ASNH_TABLE = {"name": ASNH, "kind": "transaction", "proposed": True,
              "description": "ASN header of ASN Crossdock Creation; its cases are in TB_R_ASN_CROSSDOCK_D. Name and columns proposed.",
              "columns": ASNH_COLS}

ASND_COLS = [
    ["ASN_NO", "VARCHAR(TBD)", "Y", "N", "ASN number (TB_R_ASN_CROSSDOCK_H)"],
    ["CASE_NO", "VARCHAR(TBD)", "Y", "N", "Case number; format and sequence follow the existing numbering (last sequence table)"],
    ["LINE_SEQ", "NUMBER(4)", "Y", "N", "Order line x PO within the case"],
    ["PART_NO", "VARCHAR(15)", "", "N", "Part number of the case"],
    ["ORDER_DT", "DATE", "", "N", "Customer Order Date"],
    ["DESTINATION_CD", "VARCHAR(7)", "", "N", "Destination of the case"],
    ["CUSTOMER_CD", "VARCHAR(7)", "", "N", "Customer code"],
    ["CUSTOMER_ORDER_NO", "VARCHAR(8)", "", "N", "Customer order number"],
    ["DETAILED_ITEM_NO", "VARCHAR(4)", "", "N", "Detailed item number"],
    ["SERIAL_NO", "VARCHAR(7)", "", "N", "Serial number"],
    ["QTY", "NUMBER(8)", "", "N", "Qty of the line in the case"],
    ["PO_NO", "VARCHAR(TBD)", "", "N", "PO number"],
    ["MANIFEST_NO", "VARCHAR(TBD)", "", "N", "Manifest number"],
    ["MANIFEST_ITEM_NO", "VARCHAR(TBD)", "", "N", "Manifest item number"],
    ["PO_ORDER_QTY", "NUMBER(TBD)", "", "N", "PO qty"],
    ["CREATED_BY", "VARCHAR(TBD)", "", "N", "User who submitted the ASN"],
    ["CREATED_DT", "DATETIME", "", "N", "Submit date and time"],
    ["CHANGED_BY", "VARCHAR(TBD)", "", "N", "User who last changed the record"],
    ["CHANGED_DT", "DATETIME", "", "N", "Last changed date and time"]]
ASND_TABLE = {"name": ASND, "kind": "transaction", "proposed": True,
              "description": "Cases of a submitted ASN: one row per case x order line x PO. Name and columns proposed.",
              "columns": ASND_COLS}


def it(name, source='', field='', type_='', len_='', io='', control='', just='', init='', req='', fmt='', val='', desc=''):
    return {"name": name, "source": source, "field": field, "type": type_, "len": len_, "io": io, "control": control,
            "justified": just, "initial": init, "required": req, "format": fmt, "validation": val, "description": desc}


def btn(name, desc, init='Enabled'):
    return it(name, '-', '-', '-', '-', 'I', 'Button', 'Center', init, 'N', '-', '-', desc)


def out(name, source, field, type_, len_, control, just, fmt, desc, init='-'):
    return it(name, source, field, type_, len_, 'O', control, just, init, 'N', fmt, '-', desc)


def header(fid, block, title, date='14-Oct-26'):
    return {"phase": "DR", "project_name": PROJ, "block_name": block, "function_name": f"{fid} {title}", "created_date": date, "created_by": NAME}


def revisions(date='14-Oct-26'):
    return [{"revision": "0.1", "author": NAME, "date": date, "reviewed_by": "", "description": "Initial Draft"}]
