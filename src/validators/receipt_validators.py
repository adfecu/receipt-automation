"""
Validators for receipt data fields (RNC, NCF, date).
"""
import re
import streamlit as st
import pandas as pd
from config import RNC_CSV_PATH


@st.cache_data(show_spinner=False)
def load_rnc_set():
    """
    Load RNCs from CSV file and return as a set for fast lookup.
    
    Returns:
        set: Set of valid RNC numbers
    """
    df = pd.read_csv(RNC_CSV_PATH, dtype=str)
    rnc_col = df.columns[0]
    return set(df[rnc_col].str.replace('-', '').dropna())


@st.cache_data(show_spinner=False)
def highlight_invalid_date(val):
    """
    Return red background if date is not in DD/MM/YYYY format.
    
    Args:
        val: Date value to validate
        
    Returns:
        str: CSS style string for invalid dates, empty string for valid dates
    """
    if not isinstance(val, str):
        return "background-color: red; color: white;"
    # Match DD/MM/YYYY format
    if not re.fullmatch(r"(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}", val):
        return "background-color: red; color: white;"
    return ""


@st.cache_data(show_spinner=False)
def highlight_invalid_rnc(val):
    """
    Return red background if RNC is invalid (not in CSV database).
    
    Args:
        val: RNC value to validate
        
    Returns:
        str: CSS style string for invalid RNCs, empty string for valid RNCs
    """
    if not val:
        return "background-color: red; color: white;"
    
    digits = str(val).replace('-', '')
    
    rnc_set = load_rnc_set()
    if digits not in rnc_set:
        return "background-color: red; color: white;"
    return ""


@st.cache_data(show_spinner=False)
def highlight_invalid_ncf(val):
    """
    Return red background if NCF is invalid according to DGII rules.
    
    Valid NCF formats:
    - B followed by 10 digits (codes 01-04, 11-17)
    - E followed by 12 digits (codes 31-34, 41, 43-47)
    
    Args:
        val: NCF value to validate
        
    Returns:
        str: CSS style string for invalid NCFs, empty string for valid NCFs
    """
    if not isinstance(val, str):
        return "background-color: red; color: white;"
    ncf = val.lstrip('0').upper()
    
    # B followed by 10 digits
    if re.fullmatch(r'B\d{10}', ncf):
        code = ncf[1:3]
        if code in [f'{i:02}' for i in range(1, 5)] or code in [f'{i:02}' for i in range(11, 18)]:
            return ""
        return "background-color: red; color: white;"
    
    # E followed by 12 digits
    if re.fullmatch(r'E\d{12}', ncf):
        code = ncf[1:3]
        if code in [f'{i:02}' for i in range(31, 35)] or code == '41' or code in [f'{i:02}' for i in range(43, 48)]:
            return ""
        return "background-color: red; color: white;"
    
    return "background-color: red; color: white;"

