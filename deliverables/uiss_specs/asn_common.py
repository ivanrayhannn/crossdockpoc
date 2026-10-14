"""Shared definitions for the ASN Crossdock documents (X8 creation screen, X12 instruction batch, X13 inquiry screen)."""

NAME, PROJ = 'FID Rayhan', 'Crossdock Optimization'
NC = 'Not changed'
INSTR, ASNH = 'TB_R_INSTRUCTION', 'TB_R_ASN_CROSSDOCK_H'
H0253, PRA_M, PRA_P = 'TB_R_H0253_ORDER_CONTROL_PRE', 'TB_R_PRA_DAILY_ORDER_MANIFEST', 'TB_R_PRA_DAILY_ORDER_PART'
DM = 'TB_M_H0125_DESTINATION'

INSTR_COLS = [
    ["INSTRUCTION_ID", "BIGINT", "Y", "N", "Running number (identity)"],
    ["CUSTOMER_CD", "VARCHAR(7)", "", "N", "H0253.CUSTOMER_CD"],
    ["CUSTOMER_ORDER_NO", "VARCHAR(8)", "", "N", "H0253.CUSTOMER_ORDER_NO"],
    ["ORDER_DT", "DATE", "", "N", "Customer Order Date (H0253.ORDER_DT)"],
    ["DESTINATION_CD", "VARCHAR(7)", "", "N", "H0253.DESTINATION_CD (TB_M_H0125_DESTINATION)"],
    ["DETAILED_ITEM_NO", "VARCHAR(4)", "", "N", "H0253.DETAILED_ITEM_NO"],
    ["SERIAL_NO", "VARCHAR(7)", "", "N", "H0253.SERIAL_NO"],
    ["PART_NO", "VARCHAR(15)", "", "N", "Order part number (H0253.SHIPPING_PART_NO)"],
    ["ORDER_STATUS", "VARCHAR(1)", "", "N", "H0253.ORDER_STATUS ('7' Cross Dock)"],
    ["CUST_ORDER_QTY", "NUMBER(8)", "", "N", "Order status qty of the customer order line (H0253.ORDER_STATUS_QTY)"],
    ["ASSIGNED_QTY", "NUMBER(8)", "", "N", "Qty of the line assigned to this PO (0 for the not-assigned row)"],
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
    ["ASN_NO", "VARCHAR(TBD)", "", "Y", "ASN number; filled by ASN Crossdock Creation [Submit ASN]"],
    ["CASE_NO", "VARCHAR(TBD)", "", "Y", "Case number; filled by ASN Crossdock Creation [Submit ASN]"],
    ["CREATED_BY", "VARCHAR(TBD)", "", "N", "User who created the record"],
    ["CREATED_DT", "DATETIME", "", "N", "Created date and time"],
    ["CHANGED_BY", "VARCHAR(TBD)", "", "N", "User who last changed the record"],
    ["CHANGED_DT", "DATETIME", "", "N", "Last changed date and time"]]
INSTR_TABLE = {"name": INSTR, "kind": "transaction", "proposed": True,
               "description": "Customer order line (H0253, order status 7) paired with a supplier PO (Pra Daily Order), FIFO by Customer Order Date. "
                              "One row per line x PO assignment, plus one row with PO_NO NULL for the qty still without a PO. Columns proposed.",
               "columns": INSTR_COLS}

ASNH_COLS = [
    ["ASN_NO", "VARCHAR(TBD)", "Y", "N", "ASN-{Supplier}-{YYMMDD of Delivery Date}-{Seq}"],
    ["SUPPLIER_CD", "VARCHAR(TBD)", "", "N", "Supplier of the cases"],
    ["SUPPLIER_PLANT", "VARCHAR(TBD)", "", "N", "Supplier plant"],
    ["DELIVERY_DT", "DATE", "", "N", "Delivery Date"],
    ["RIT_CYCLE", "VARCHAR(TBD)", "", "N", "Rit Cycle"],
    ["ROUTE", "VARCHAR(TBD)", "", "N", "Route of the Rit Cycle"],
    ["TOTAL_CASE", "NUMBER", "", "N", "Number of cases"],
    ["TOTAL_QTY", "NUMBER", "", "N", "Total pieces"],
    ["ASN_STATUS", "VARCHAR(TBD)", "", "N", "'SUBMITTED'"],
    ["CREATED_BY", "VARCHAR(TBD)", "", "N", "User who submitted the ASN"],
    ["CREATED_DT", "DATETIME", "", "N", "Submit date and time"],
    ["CHANGED_BY", "VARCHAR(TBD)", "", "N", "User who last changed the record"],
    ["CHANGED_DT", "DATETIME", "", "N", "Last changed date and time"]]
ASNH_TABLE = {"name": ASNH, "kind": "transaction", "proposed": True,
              "description": "ASN header of ASN Crossdock Creation; cases and lines are in TB_R_INSTRUCTION (ASN_NO, CASE_NO). Name and columns proposed.",
              "columns": ASNH_COLS}


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
