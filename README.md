
# 📄 606 Automático: Dominican Receipt Data Extractor

This Streamlit app extracts structured data from Dominican fiscal receipts (Comprobantes Fiscales) in images or PDFs, using Google Gemini AI. It outputs a table ready for 606 tax reporting.

## Features
- Upload multiple receipt images (`jpg`, `jpeg`, `png`, `heic`) or PDFs
- Extracts: RNC, NCF, date, subtotal, ITBIS, ISC, other taxes, tips
- Uses Google Gemini for highly accurate data extraction
- Displays results in a table for easy copy/paste to 606

## How to Run Locally
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   streamlit run streamlit_app.py
   ```

## Usage
1. Upload your receipt images or PDFs (one receipt per file)
2. Click **Generar 606**
3. View and copy the extracted data table

## Requirements
- Python 3.8+
- [Google Gemini API key](https://ai.google.dev/) (set up via `google-genai`)

## File Structure
- `streamlit_app.py`: Main Streamlit app
- `utils/prompts.py`: LLM prompt templates
- `requirements.txt`: Python dependencies

## License
Apache 2.0
