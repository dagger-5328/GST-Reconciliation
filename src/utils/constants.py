"""
Constants and configuration variables for the GST Reconciliation Tool.
"""

# --- Column Names ---
# We define these here so if the Excel headers change, we only update them in one place.
COL_GSTIN = "GSTIN"
COL_INVOICE_NO = "Invoice Number"
COL_INVOICE_DATE = "Invoice Date"
COL_TAXABLE_VALUE = "Taxable Value"
COL_IGST = "IGST"
COL_CGST = "CGST"
COL_SGST = "SGST"
COL_TOTAL_AMOUNT = "Total Amount"

# --- Regex Patterns ---
# Standard GSTIN format: 2 digits (State), 5 letters (PAN), 4 digits, 1 letter, 1 alphanumeric, 'Z', 1 alphanumeric
GSTIN_REGEX = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"

# Pattern to strip out slashes, dashes, and spaces from invoice numbers
INVOICE_STRIP_REGEX = r"[^a-zA-Z0-9]"

# --- Matching Thresholds ---
# If fuzzy matching score is below this (0-100), we flag it for manual review
FUZZY_MATCH_THRESHOLD = 85 

# --- File Paths ---
# We'll use these later in the Streamlit app
DATA_RAW_DIR = "data/raw"
DATA_PROCESSED_DIR = "data/processed"

# --- Column Aliases for Auto-Mapping ---
# These are common variations of column names found in different accounting software
COLUMN_ALIASES = {
    COL_GSTIN: [
        "gstin", "gst no", "gst number", "supplier gstin", "vendor gstin", 
        "tax id", "gstin of supplier", "customer gstin"
    ],
    COL_INVOICE_NO: [
        "invoice number", "invoice no", "inv no", "bill no", "document number", 
        "invoice", "voucher no", "invoice_number"
    ],
    COL_TOTAL_AMOUNT: [
        "total amount", "invoice value", "total value", "amount", "grand total", 
        "total invoice value", "total_amount"
    ]
}