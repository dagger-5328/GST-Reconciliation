import pandas as pd
from rapidfuzz import process, fuzz
from src.utils.constants import COLUMN_ALIASES

def auto_map_columns(df: pd.DataFrame, threshold: int = 85) -> dict:
    """
    Automatically maps the columns of a DataFrame to our standard column names.
    Returns a dictionary: { 'Detected Column Name': 'Standard Column Name' }
    """
    detected_mapping = {}
    df_columns = df.columns.tolist()
    
    for standard_col, aliases in COLUMN_ALIASES.items():
        # Create a list of all possible search terms (the standard name + aliases)
        search_terms = [standard_col.lower()] + [a.lower() for a in aliases]
        
        best_match = None
        highest_score = 0
        
        for df_col in df_columns:
            # Compare the DataFrame column against all search terms
            # We use token_set_ratio because it handles extra words well (e.g., "Supplier GSTIN No")
            match = process.extractOne(
                str(df_col).lower(), 
                search_terms, 
                scorer=fuzz.WRatio
            )
            
            if match and match[1] > highest_score and match[1] >= threshold:
                highest_score = match[1]
                best_match = df_col
                
        if best_match:
            detected_mapping[best_match] = standard_col
            print(f"[INFO] Auto-mapped '{best_match}' -> '{standard_col}' (Score: {highest_score})")
        else:
            print(f"[WARNING] Could not find a match for standard column '{standard_col}'")

    return detected_mapping

def apply_column_mapping(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    """
    Renames the DataFrame columns based on the mapping dictionary.
    """
    return df.rename(columns=mapping)