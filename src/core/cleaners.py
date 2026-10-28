import re
import pandas as pd
from typing import Optional
from src.utils.constants import GSTIN_REGEX, INVOICE_STRIP_REGEX

def clean_gstin(gstin: str) -> str:
    """
    Cleans a GSTIN by converting to uppercase and removing spaces/special characters.
    Returns empty string if input is invalid or NaN.
    """
    if pd.isna(gstin) or not isinstance(gstin, str):
        return ""
    
    # Uppercase and remove all non-alphanumeric characters
    clean_str = re.sub(r'[^A-Z0-9]', '', gstin.upper())
    
    # Basic length check (GSTINs are exactly 15 characters)
    if len(clean_str) == 15:
        return clean_str
    return clean_str # Return anyway, but the validator will catch it later

def clean_invoice_number(inv_no: str) -> str:
    """
    Normalizes invoice numbers by uppercasing and removing slashes, dashes, spaces.
    Example: 'INV/23-24/001' -> 'INV2324001'
    """
    if pd.isna(inv_no):
        return ""
    
    # Convert to string, uppercase, and remove unwanted characters
    inv_str = str(inv_no).upper().strip()
    clean_str = re.sub(INVOICE_STRIP_REGEX, "", inv_str)
    
    return clean_str

def parse_amount(amount) -> Optional[float]:
    """
    Safely converts a value to a float.
    Handles strings like '1,000.50', 'Rs. 500', or empty values.
    """
    if pd.isna(amount):
        return None
    if isinstance(amount, (int, float)):
        return float(amount)
    
    # Remove commas, currency symbols, and spaces from strings
    amount_str = str(amount).replace(',', '').replace('₹', '').replace('Rs.', '').strip()
    
    try:
        return float(amount_str)
    except ValueError:
        return None

def clean_dataframe(df: pd.DataFrame, gstin_col: str, inv_col: str, amount_col: str) -> pd.DataFrame:
    """
    Applies all cleaning functions to a DataFrame.
    Takes column names as arguments so it works for both GSTR-2B and Purchase Register.
    """
    # Create a copy to avoid SettingWithCopyWarning
    df_clean = df.copy()
    
    # Apply the cleaning functions
    df_clean[gstin_col] = df_clean[gstin_col].apply(clean_gstin)
    df_clean[inv_col] = df_clean[inv_col].apply(clean_invoice_number)
    df_clean[amount_col] = df_clean[amount_col].apply(parse_amount)
    
    # Drop rows where the invoice number is empty (junk rows)
    df_clean = df_clean[df_clean[inv_col] != ""]
    
    return df_clean