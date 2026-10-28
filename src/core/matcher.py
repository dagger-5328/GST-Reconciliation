import pandas as pd
from rapidfuzz import process, fuzz
from src.utils.constants import FUZZY_MATCH_THRESHOLD

def perform_exact_match(df_books: pd.DataFrame, df_2b: pd.DataFrame, gstin_col: str, inv_col: str) -> pd.DataFrame:
    """
    Performs a strict exact match on GSTIN and Invoice Number.
    Returns a merged dataframe.
    """
    # We do an inner merge to keep only records that exist in BOTH files
    merged_df = pd.merge(
        df_books, 
        df_2b, 
        on=[gstin_col, inv_col], 
        how='inner', 
        suffixes=('_books', '_2b')
    )
    return merged_df

def perform_fuzzy_match(df_books_unmatched: pd.DataFrame, df_2b_unmatched: pd.DataFrame, gstin_col: str, inv_col: str) -> pd.DataFrame:
    """
    Performs fuzzy matching on unmatched records.
    It looks for the best match in df_2b for every record in df_books.
    """
    matches = []
    
    # Create a list of tuples for fast lookup: (GSTIN, Invoice_No)
    choices = list(zip(df_2b_unmatched[gstin_col], df_2b_unmatched[inv_col]))
    
    for index, row in df_books_unmatched.iterrows():
        book_gstin = row[gstin_col]
        book_inv = row[inv_col]
        book_key = f"{book_gstin}_{book_inv}"
        
        # Extract the best match from the 2B choices based on the book_key
        # We use token_sort_ratio because it handles rearranged words/numbers well
        best_match = process.extractOne(
            book_key, 
            [f"{g}_{i}" for g, i in choices], 
            scorer=fuzz.token_sort_ratio,
            score_cutoff=FUZZY_MATCH_THRESHOLD
        )
        
        if best_match:
            match_string, score, match_index = best_match
            matched_gstin, matched_inv = match_string.split('_')
            
            matches.append({
                'book_index': index,
                'matched_gstin': matched_gstin,
                'matched_inv': matched_inv,
                'score': score
            })
            
    return pd.DataFrame(matches)

def reconcile_data(df_books: pd.DataFrame, df_2b: pd.DataFrame, gstin_col: str, inv_col: str) -> dict:
    """
    The main entry point. Runs exact match, then fuzzy match on the leftovers.
    Returns a dictionary containing matched, unmatched_books, and unmatched_2b.
    """
    print("[INFO] Starting Exact Match...")
    exact_matches = perform_exact_match(df_books, df_2b, gstin_col, inv_col)
    print(f"[INFO] Exact matches found: {len(exact_matches)}")
    
    # Get the records that DID NOT match exactly
    df_books['temp_key'] = df_books[gstin_col] + "_" + df_books[inv_col]
    exact_keys = set(exact_matches[gstin_col] + "_" + exact_matches[inv_col])
    
    df_books_unmatched = df_books[~df_books['temp_key'].isin(exact_keys)].drop(columns=['temp_key'])
    
    df_2b['temp_key'] = df_2b[gstin_col] + "_" + df_2b[inv_col]
    df_2b_unmatched = df_2b[~df_2b['temp_key'].isin(exact_keys)].drop(columns=['temp_key'])
    
    print(f"[INFO] Books unmatched after exact match: {len(df_books_unmatched)}")
    print(f"[INFO] 2B unmatched after exact match: {len(df_2b_unmatched)}")
    
    print("[INFO] Starting Fuzzy Match on unmatched records...")
    fuzzy_matches = perform_fuzzy_match(df_books_unmatched, df_2b_unmatched, gstin_col, inv_col)
    print(f"[INFO] Fuzzy matches found: {len(fuzzy_matches)}")
    
    # --- NEW FIX: Remove fuzzy matched records from the unmatched pools ---
    if not fuzzy_matches.empty:
        # Get the indices of records in books that were fuzzily matched
        matched_book_indices = fuzzy_matches['book_index'].tolist()
        
        # Get the GSTIN and Invoice of the 2B records that were matched
        matched_2b_keys = fuzzy_matches['matched_gstin'] + "_" + fuzzy_matches['matched_inv']
        
        # Filter out the matched records
        df_books_unmatched = df_books_unmatched.drop(matched_book_indices)
        
        df_2b_unmatched['temp_key'] = df_2b_unmatched[gstin_col] + "_" + df_2b_unmatched[inv_col]
        df_2b_unmatched = df_2b_unmatched[~df_2b_unmatched['temp_key'].isin(matched_2b_keys)].drop(columns=['temp_key'])
    # ---------------------------------------------------------------------

    return {
        "exact_matches": exact_matches,
        "fuzzy_matches": fuzzy_matches,
        "unmatched_books": df_books_unmatched,
        "unmatched_2b": df_2b_unmatched
    }