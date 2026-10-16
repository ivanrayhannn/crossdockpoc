"""Shared definitions for the ASN Crossdock documents (X8 creation screen, X12 instruction batch, X13 inquiry screen)."""

NAME, PROJ = 'FID Rayhan', 'Crossdock Optimization'
NC = 'Not changed'
INSTR, ASNH, ASND, DRAFT = '#TEMP_INSTRUCTION', 'TB_R_DAILY_ORDER_MANIFEST', 'TB_R_DAILY_ORDER_PART', 'TB_R_INSTRUCTION'
PRA_MAP = 'TB_R_PRA_DAILY_ORDER_MAPPED'
ROUTE_M = 'Route master (existing)'
LAST_SEQ = 'Last sequence table (existing)'
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
               "description": "Temporary table of one Search run (session): customer order line (H0253, order status 7, Hold Flag N, not mapped) "
                              "pre-mapped to a supplier PO (Pra Daily Order), FIFO by order date. One row per line x PO, plus one row with PO_NO NULL "
                              "for the qty still without a PO. Columns proposed.",
               "columns": INSTR_COLS}

DRAFT_COLS = [
    ["INSTRUCTION_ID", "BIGINT", "Y", "N", "Running number (identity)"],
    ["SUPPLIER_CD", "VARCHAR(TBD)", "", "N", "Supplier code (one ASN = one Supplier Code + Plant)"],
    ["SUPPLIER_PLANT", "VARCHAR(TBD)", "", "N", "Supplier plant"],
    ["CASE_SEQ", "NUMBER(4)", "", "N", "Case sequence of the Create ASN (Case 1, 2, ...)"],
    ["LINE_SEQ", "NUMBER(4)", "", "N", "Order line x PO within the case"],
    ["PART_NO", "VARCHAR(15)", "", "N", "Part number of the case"],
    ["ORDER_DT", "DATE", "", "N", "Customer Order Date of the case"],
    ["DESTINATION_CD", "VARCHAR(7)", "", "N", "Destination of the case"],
    ["CUSTOMER_CD", "VARCHAR(7)", "", "N", "Customer code"],
    ["CUSTOMER_ORDER_NO", "VARCHAR(8)", "", "N", "Customer order number"],
    ["DETAILED_ITEM_NO", "VARCHAR(4)", "", "N", "Detailed item number"],
    ["SERIAL_NO", "VARCHAR(7)", "", "N", "Serial number"],
    ["QTY", "NUMBER(8)", "", "N", "Qty of the line mapped to the PO in this case"],
    ["PO_NO", "VARCHAR(TBD)", "", "N", "PO number"],
    ["MANIFEST_NO", "VARCHAR(TBD)", "", "N", "Manifest number of the Pra Daily Order"],
    ["MANIFEST_ITEM_NO", "VARCHAR(TBD)", "", "N", "Manifest item number"],
    ["PO_ORDER_QTY", "NUMBER(TBD)", "", "N", "PO qty"],
    ["DELIVERY_DT", "DATE", "", "N", "Delivery Date of the Search"],
    ["RIT_CYCLE", "VARCHAR(TBD)", "", "N", "Rit of the Search (route master, existing)"],
    ["ROUTE", "VARCHAR(TBD)", "", "N", "Route of the Rit (route master, existing)"],
    ["ASN_NO", "VARCHAR(TBD)", "", "Y", "ASN number; NULL until the ASN is submitted (X14)"],
    ["CASE_NO", "VARCHAR(TBD)", "", "Y", "Case number; NULL until submitted (auto generated with the existing last sequence)"],
    ["CREATED_BY", "VARCHAR(TBD)", "", "N", "User who created the record"],
    ["CREATED_DT", "DATETIME", "", "N", "Created date and time"],
    ["CHANGED_BY", "VARCHAR(TBD)", "", "N", "User who last changed the record"],
    ["CHANGED_DT", "DATETIME", "", "N", "Last changed date and time"]]
DRAFT_TABLE = {"name": DRAFT, "kind": "transaction", "proposed": True,
               "description": "Real mapping made by [Create ASN]: one row per case x customer order line x PO of the selected units. Rows are deleted by [Back] / [Cancel] on the Case List; [Submit ASN] (X14) fills ASN_NO and CASE_NO. Columns proposed.",
               "columns": DRAFT_COLS}

PRA_MAP_COLS = [
    ["PO_NO", "VARCHAR(TBD)", "Y", "N", "PO number (Pra Daily Order Manifest)"],
    ["MANIFEST_NO", "VARCHAR(TBD)", "Y", "N", "Manifest number"],
    ["MANIFEST_ITEM_NO", "VARCHAR(TBD)", "Y", "N", "Manifest item number (Pra Daily Order Part)"],
    ["PART_NO", "VARCHAR(15)", "", "N", "Part number"],
    ["SUPPLIER_CD", "VARCHAR(TBD)", "", "N", "Supplier code"],
    ["SUPPLIER_PLANT", "VARCHAR(TBD)", "", "N", "Supplier plant"],
    ["PO_ORDER_QTY", "NUMBER(TBD)", "", "N", "PO qty of the part"],
    ["MAPPED_QTY", "NUMBER(TBD)", "", "N", "Qty already mapped to customer orders by [Create ASN]; open qty = PO_ORDER_QTY - MAPPED_QTY"],
    ["CREATED_BY", "VARCHAR(TBD)", "", "N", "User who created the record"],
    ["CREATED_DT", "DATETIME", "", "N", "Created date and time"],
    ["CHANGED_BY", "VARCHAR(TBD)", "", "N", "User who last changed the record"],
    ["CHANGED_DT", "DATETIME", "", "N", "Last changed date and time"]]
PRA_MAP_TABLE = {"name": PRA_MAP, "kind": "transaction", "proposed": True,
                 "description": "New table: mapped qty per Pra Daily Order PO part (instead of a new column in the Pra Daily Order). Name and columns proposed.",
                 "columns": PRA_MAP_COLS}

ASNH_COLS = [
    ["MANIFEST_NO / ASN_NO", "existing", "Y", "N", "ASN number (auto generated as today, existing numbering)"],
    ["SUPPLIER_CD", "existing", "", "N", "Supplier code"],
    ["SUPPLIER_PLANT", "existing", "", "N", "Supplier plant"],
    ["DELIVERY_DT", "existing", "", "N", "Delivery Date"],
    ["RIT / ROUTE", "existing", "", "N", "Rit and route (route master, existing)"],
    ["TOTAL_CASE / TOTAL_QTY", "existing", "", "N", "Number of cases / Delivery Qty"],
    ["STATUS", "existing", "", "N", "Created"],
    ["CREATED_BY / CREATED_DT", "existing", "", "N", "User and date-time of submit"]]
ASNH_TABLE = {"name": ASNH, "kind": "transaction", "proposed": False,
              "description": "Existing ASN header table of NSP; the crossdock ASN is saved here after submit. Only the fields used are listed; physical names follow the existing table.",
              "columns": ASNH_COLS}

ASND_COLS = [
    ["MANIFEST_NO / ASN_NO", "existing", "Y", "N", "ASN number"],
    ["CASE_NO", "existing", "Y", "N", "Case number, auto generated with the existing last sequence"],
    ["PART_NO", "existing", "", "N", "Part number of the case"],
    ["DESTINATION_CD", "existing", "", "N", "Destination of the case"],
    ["QTY", "existing", "", "N", "Qty of the case"],
    ["PO_NO / MANIFEST_ITEM_NO", "existing", "", "N", "PO reference of the Pra Daily Order"],
    ["CREATED_BY / CREATED_DT", "existing", "", "N", "User and date-time of submit"]]
ASND_TABLE = {"name": ASND, "kind": "transaction", "proposed": False,
              "description": "Existing ASN part / case table of NSP. Only the fields used are listed; physical names follow the existing table.",
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
