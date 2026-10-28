import streamlit as st
import pandas as pd
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.cleaners import clean_dataframe
from src.core.matcher import reconcile_data
from src.core.reporter import generate_excel_report
from src.core.schema_mapper import auto_map_columns, apply_column_mapping
from src.utils.constants import (
    COL_GSTIN, COL_INVOICE_NO, COL_TOTAL_AMOUNT,
    DATA_PROCESSED_DIR
)

st.set_page_config(page_title="GST Reconciliation Tool", page_icon="📊", layout="wide")

st.title("GST Reconciliation Tool")
st.markdown("Upload your Purchase Register and GSTR-2B files to reconcile invoices.")

# Helper function to read either CSV or Excel
def load_data(file):
    if file.name.lower().endswith('.csv'):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

# Sidebar for file uploads
with st.sidebar:
    st.header("Upload Files")
    books_file = st.file_uploader("Purchase Register (Excel/CSV)", type=["xlsx", "xls", "csv"])
    portal_file = st.file_uploader("GSTR-2B (Excel/CSV)", type=["xlsx", "xls", "csv"])
    
    st.markdown("---")
    st.markdown("### Column Mapping")
    st.info("The tool auto-detects columns, but expects: GSTIN, Invoice Number, Total Amount")

if books_file and portal_file:
    try:
        # 1. Load the files
        df_books_raw = load_data(books_file)
        df_2b_raw = load_data(portal_file)
        
        # 2. Auto-map the columns
        with st.spinner("Auto-detecting columns..."):
            books_mapping = auto_map_columns(df_books_raw)
            df_books = apply_column_mapping(df_books_raw, books_mapping)
            
            portal_mapping = auto_map_columns(df_2b_raw)
            df_2b = apply_column_mapping(df_2b_raw, portal_mapping)
            
        st.info(f"Auto-detected Books Columns: {books_mapping}")
        
        # 3. Clean the data
        with st.spinner("Cleaning data..."):
            df_books_clean = clean_dataframe(df_books, COL_GSTIN, COL_INVOICE_NO, COL_TOTAL_AMOUNT)
            df_2b_clean = clean_dataframe(df_2b, COL_GSTIN, COL_INVOICE_NO, COL_TOTAL_AMOUNT)
            
        st.success(f"Data Loaded: {len(df_books_clean)} books records, {len(df_2b_clean)} portal records.")
        
        # 4. The Missing Button (Now included and set to primary color)
        if st.button("Run Reconciliation", type="primary"):
            with st.spinner("Matching invoices..."):
                results = reconcile_data(df_books_clean, df_2b_clean, COL_GSTIN, COL_INVOICE_NO)
                
            st.markdown("### Results Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("Exact Matches", len(results['exact_matches']))
            col2.metric("Fuzzy Matches", len(results['fuzzy_matches']))
            col3.metric("Mismatches", len(results['unmatched_books']) + len(results['unmatched_2b']))
            
            # Show the missing records
            st.markdown("### Mismatched Records (Needs Review)")
            tab1, tab2 = st.tabs(["Missing in Portal", "Missing in Books"])
            with tab1:
                st.dataframe(results['unmatched_books'])
            with tab2:
                st.dataframe(results['unmatched_2b'])
            
            # Generate and download report
            with st.spinner("Generating Excel report..."):
                report_path = generate_excel_report(results)
                with open(report_path, "rb") as f:
                    st.download_button(
                        label="Download Excel Report",
                        data=f,
                        file_name=os.path.basename(report_path),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
else:
    st.info("Please upload both files to begin.")