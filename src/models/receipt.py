"""
Data models for receipt information.
"""
from pydantic import BaseModel


class ReceiptData(BaseModel):
    """
    Data model for a Dominican fiscal receipt.
    
    Attributes:
        rnc_vendor: Vendor RNC number
        ncf: Full alphanumeric NCF string (e.g., B0100055276)
        date: Receipt date in DD/MM/YYYY format
        subtotal: Calculated subtotal (total - itbis)
        itbis: ITBIS tax amount
        isc: Selective Consumption Tax amount
        tips: Legal tip amount
    """
    rnc_vendor: int
    ncf: str
    date: str
    subtotal: float
    itbis: float
    isc: float
    tips: float

