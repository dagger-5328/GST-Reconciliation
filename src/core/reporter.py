import pandas as pd
from datetime import datetime
import os
from src.utils.constants import DATA_PROCESSED_DIR

def generate_excel_report(reconciliation_results: dict, output_filename: str = None) -> str:
    """
    Generates a formatted Excel report from the reconciliation results.
    Creates separate sheets for Matches, Missing in 2B, and Missing in Books.
    """
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"GST_Reconciliation_Report_{timestamp}.xlsx"
        
    # Ensure output directory exists
    os.makedirs(DATA_PROCESSED_DIR, exist_ok=True)
    output_path = os.path.join(DATA_PROCESSED_DIR, output_filename)
    
    print(f"[INFO] Generating Excel report at: {output_path}")
    
    # Create a Pandas Excel writer using XlsxWriter as the engine
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Define formats
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D9E1F2', 'border': 1})
        
        # 1. Write the Matched sheet
        exact = reconciliation_results.get('exact_matches', pd.DataFrame())
        
        if not exact.empty:
            exact.to_excel(writer, sheet_name='Matched_Invoices', index=False)
            worksheet = writer.sheets['Matched_Invoices']
            for col_num, value in enumerate(exact.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 20)
                
        # 2. Write Missing in 2B (In Books but not in Portal)
        missing_2b = reconciliation_results.get('unmatched_books', pd.DataFrame())
        if not missing_2b.empty:
            missing_2b.to_excel(writer, sheet_name='Missing_in_Portal', index=False)
            worksheet = writer.sheets['Missing_in_Portal']
            for col_num, value in enumerate(missing_2b.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 20)

        # 3. Write Missing in Books (In Portal but not in Books)
        missing_books = reconciliation_results.get('unmatched_2b', pd.DataFrame())
        if not missing_books.empty:
            missing_books.to_excel(writer, sheet_name='Missing_in_Books', index=False)
            worksheet = writer.sheets['Missing_in_Books']
            for col_num, value in enumerate(missing_books.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 20)

    print("[SUCCESS] Excel report generated successfully.")
    return output_path