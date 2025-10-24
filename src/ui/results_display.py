"""
UI components for displaying receipt extraction results.
"""
import pandas as pd
import streamlit as st
from src.validators.receipt_validators import (
    highlight_invalid_date,
    highlight_invalid_rnc,
    highlight_invalid_ncf
)


def display_results(uploaded_files, responses_list):
    """
    Processes the responses, flattens them, adds file_name, and displays a styled dataframe.
    
    Args:
        uploaded_files: List of uploaded file objects
        responses_list: List of LLM responses (one per file)
    """
    valid_responses = [r for r in responses_list if r and not isinstance(r, Exception)]
    
    # Flatten the list of lists (if each response is a list of dicts) and add file_name
    flattened = []
    for uploaded_file, response in zip(uploaded_files, valid_responses):
        if response:
            for row in response:
                row["file_name"] = uploaded_file.name
                flattened.append(row)
    
    if flattened:
        df = pd.DataFrame(flattened)
        
        # Remove leading zeros from NCF codes
        if 'ncf' in df.columns:
            df['ncf'] = df['ncf'].astype(str).str.lstrip('0').str.upper()

        # Apply style to rnc_vendor, ncf, and date columns
        styled_df = df.style\
            .map(highlight_invalid_rnc, subset=["rnc_vendor"])\
            .map(highlight_invalid_ncf, subset=["ncf"])\
            .map(highlight_invalid_date, subset=["date"])
        
        st.dataframe(
            styled_df,
            hide_index=True,
            column_config={
                "subtotal": st.column_config.NumberColumn("Subtotal", format="accounting"),
                "itbis": st.column_config.NumberColumn("ITBIS", format="accounting"),
                "tips": st.column_config.NumberColumn("Propina", format="accounting"),
                "isc": st.column_config.NumberColumn("ISC", format="accounting"),
            }
        )
    else:
        st.info("No valid JSON responses were generated to display in the table.")

