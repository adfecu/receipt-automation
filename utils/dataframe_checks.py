import re
import streamlit as st

@st.cache_data(show_spinner=False)
def highlight_invalid_rnc(val):
    """Return red background if RNC is invalid (consulta_rnc returns None)."""
    if not val:
        return "background-color: red; color: white;"
    digits = str(val).replace('-', '')
    if not digits.isdigit() or len(digits) not in (9, 11):
        return "background-color: red; color: white;"
    return ""

@st.cache_data(show_spinner=False)
def highlight_invalid_ncf(val):
    """Return red background if NCF is invalid according to rules."""
    if not isinstance(val, str):
        return "background-color: red; color: white;"
    ncf = val.lstrip('0').upper()
    # B followed by 10 digits, E followed by 12 digits
    if re.fullmatch(r'B\d{10}', ncf):
        code = ncf[1:3]
        if code in [f'{i:02}' for i in range(1, 5)] or code in [f'{i:02}' for i in range(11, 18)]:
            return ""
        return "background-color: red; color: white;"
    if re.fullmatch(r'E\d{12}', ncf):
        code = ncf[1:3]
        if code in [f'{i:02}' for i in range(31, 35)] or code == '41' or code in [f'{i:02}' for i in range(43, 48)]:
            return ""
        return "background-color: red; color: white;"
    return "background-color: red; color: white;"
