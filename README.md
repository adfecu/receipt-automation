# 📄 606 Automático: Dominican Receipt Data Extractor

A professional Streamlit application that extracts structured data from Dominican fiscal receipts (Comprobantes Fiscales) using Google Gemini AI. The app processes images and PDFs to automatically extract receipt information and outputs a table ready for 606 tax reporting.

## Features

- **Multi-File Upload**: Process multiple receipt images (`jpg`, `jpeg`) or PDFs simultaneously
- **Advanced AI Extraction**: Uses Google Gemini 2.5 Flash for highly accurate data extraction
- **Intelligent Preprocessing**: Automatic receipt detection, cropping, and contrast enhancement
- **Comprehensive Data Extraction**:
  - RNC (Vendor Tax ID)
  - NCF (Tax Receipt Number)
  - Date (DD/MM/YYYY format)
  - Subtotal (calculated automatically)
  - ITBIS (VAT tax)
  - ISC (Selective Consumption Tax)
  - Legal Tips
- **Data Validation**: Real-time validation of RNC, NCF, and date formats with visual highlighting
- **606 Format Ready**: Results displayed in a table optimized for easy copy/paste to 606 tax reports

## Project Structure

```
receipt-automation/
├── .gitignore                  # Git ignore patterns
├── LICENSE                     # Apache 2.0 license
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── config.py                   # Centralized configuration
├── streamlit_app.py            # Main application entry point
├── data/                       # Data files
│   └── RNC_Contribuyentes_Actualizado_30_Ago_2025.csv
├── src/                        # Main application source
│   ├── models/                 # Data models
│   │   └── receipt.py         # ReceiptData model
│   ├── services/               # Business logic
│   │   ├── llm_service.py     # LLM processing
│   │   ├── image_service.py   # Image preprocessing
│   │   └── dgii_service.py    # DGII API integration
│   ├── validators/             # Validation logic
│   │   └── receipt_validators.py  # RNC, NCF, date validation
│   ├── prompts/                # Prompt templates
│   │   └── extraction_prompts.py
│   └── ui/                     # UI components
│       └── results_display.py # Results table display
└── scripts/                    # Development/utility scripts
    ├── test_bboxes.py         # Bounding box detection test
    └── test_enhance.py        # Image enhancement test
```

## Requirements

- Python 3.8+
- [Google Gemini API key](https://ai.google.dev/)
- Internet connection for DGII RNC validation

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd receipt-automation
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key**:
   
   **For local development** (choose one):
   - Create a `.env` file in the project root:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```
   - Or set as environment variable:
     ```bash
     export GEMINI_API_KEY=your_api_key_here  # Linux/Mac
     set GEMINI_API_KEY=your_api_key_here     # Windows
     ```
   
   **For Streamlit Cloud deployment**:
   - Add to `.streamlit/secrets.toml`:
     ```toml
     GEMINI_API_KEY = "your_api_key_here"
     ```

## Usage

1. **Run the application**:
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Upload receipts**:
   - Click the upload button
   - Select one or more receipt images or PDFs
   - Each file should contain a single receipt

3. **Generate 606 data**:
   - Click the "Generar 606" button
   - Wait for processing (progress bar will show status)
   - Review the extracted data table

4. **Validate and export**:
   - Invalid data is highlighted in red
   - Copy the table directly to your 606 reporting tool
   - Fix any highlighted errors manually if needed

## Configuration

All configuration settings are centralized in `config.py`:

- `GEMINI_MODEL`: The Gemini model used for extraction (default: "gemini-2.5-flash")
- `GEMINI_MODEL_LITE`: The lite model for image preprocessing (default: "gemini-2.5-flash-lite")
- `CONTRAST_ENHANCEMENT_FACTOR`: Image contrast enhancement factor (default: 2)
- `BBOX_EXPANSION_FACTOR`: Bounding box expansion percentage (default: 0.05)
- `SUPPORTED_FILE_TYPES`: Allowed file upload types

## How It Works

1. **Image Preprocessing**:
   - Images are automatically oriented using EXIF data
   - Receipt bounding boxes are detected using AI
   - Images are cropped to receipt area
   - Contrast is enhanced for better OCR accuracy

2. **Data Extraction**:
   - Gemini AI processes each receipt (image or PDF)
   - Structured data is extracted using specialized prompts
   - Subtotal is calculated automatically (total - ITBIS)
   - Results are validated against DGII rules

3. **Validation**:
   - RNC numbers are validated against official DGII database
   - NCF format is validated according to DGII rules
   - Dates are validated for DD/MM/YYYY format
   - Invalid entries are highlighted in red

## Development

### Running Tests

Development scripts are located in the `scripts/` directory:

```bash
# Test bounding box detection
python scripts/test_bboxes.py

# Test contrast enhancement
python scripts/test_enhance.py
```

### Project Architecture

The application follows a modular architecture with clear separation of concerns:

- **Models**: Pydantic data models for type safety
- **Services**: Business logic for LLM, image processing, and external APIs
- **Validators**: Data validation and highlighting logic
- **Prompts**: Centralized prompt templates
- **UI**: Streamlit UI components

### Adding New Features

1. **New data fields**: Update `src/models/receipt.py` and extraction prompts
2. **New validations**: Add to `src/validators/receipt_validators.py`
3. **New services**: Create in appropriate `src/services/` module
4. **UI changes**: Modify `src/ui/results_display.py`

## Troubleshooting

### API Key Issues
- **Error**: "GEMINI_API_KEY not found"
- **Solution**: Ensure your API key is set in `.env`, environment variables, or `.streamlit/secrets.toml`

### Import Errors
- **Error**: "ModuleNotFoundError: No module named 'src'"
- **Solution**: Ensure you're running from the project root directory

### RNC Validation Issues
- **Error**: RNC highlighted as invalid but is correct
- **Solution**: Update the `data/RNC_Contribuyentes_Actualizado_30_Ago_2025.csv` file with latest data

### Image Processing Errors
- **Error**: "No se pudo preprocesar"
- **Solution**: The app will fall back to using the original image. This is usually fine.

## Security Notes

- Never commit `.env` files or API keys to version control
- The `.gitignore` file is configured to exclude sensitive files
- Use `.env.example` as a template for required environment variables

## License

Apache 2.0

## Support

For issues or questions, please open an issue on the repository.

## Acknowledgments

- Powered by [Google Gemini AI](https://ai.google.dev/)
- Built with [Streamlit](https://streamlit.io/)
- RNC validation data from [DGII](https://dgii.gov.do/)
