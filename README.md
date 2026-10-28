# GST Reconciliation Automation Tool

A Python-based tool that automates the reconciliation of a company's internal Purchase Register against the government's GSTR-2B portal data. 

## The Problem
Reconciling GST invoices manually in Excel is slow, error-prone, and struggles with messy data (e.g., `INV/23-24/1` vs `INV-23-24-1`). Businesses lose thousands in Input Tax Credit (ITC) due to unmatched invoices.

## The Solution
This tool provides a Streamlit web interface that:
1. **Auto-maps columns** using fuzzy string matching (RapidFuzz), so it works with any accounting software export.
2. **Normalizes data** (strips spaces, standardizes GSTINs, parses currency).
3. **Performs Exact & Fuzzy matching** to catch typos in invoice numbers.
4. **Generates a color-coded Excel Report** summarizing Exact Matches, Missing in Portal, and Missing in Books.

## Tech Stack
- **Frontend:** Streamlit
- **Data Processing:** Pandas, Regular Expressions
- **Matching Engine:** RapidFuzz
- **Excel Reporting:** XlsxWriter
- **Package Manager:** uv

## How to Run Locally
1. Clone the repo: `git clone https://github.com/yourusername/gst-reconciliation-tool.git`
2. Create environment: `uv venv`
3. Activate: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Mac/Linux)
4. Install dependencies: `uv pip install -r requirements.txt`
5. Run the app: `streamlit run app/main.py`

## Screenshots
*(Take a screenshot of your Streamlit app and drag it into this README file on GitHub later!)*