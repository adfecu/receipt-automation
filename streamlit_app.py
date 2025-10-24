import asyncio
import streamlit as st
from google import genai
from src.ui.results_display import display_results
from src.services.llm_service import process_files
from config import get_gemini_api_key, SUPPORTED_FILE_TYPES

st.set_page_config(
    page_title="606 automático",
    page_icon="📄",
    menu_items={
        'About': "606 automático es una app que te ayuda a convertir tus facturas al formato de envío 606 con tan solo subir fotos o PDFs de tus facturas."
    }
)

def login_screen():
    st.header("This app is private.")
    st.subheader("Please log in.")
    st.button("Log in with Google", on_click=st.login)

@st.cache_resource
def get_genai_client():
    """Initialize and cache the GenAI client."""
    return genai.Client(api_key=get_gemini_api_key())

# ---------- STREAMLIT APP ----------
def main():
    st.markdown("<h1 style='text-align: center;'>📄 606 automático</h1>", unsafe_allow_html=True)

    # Initialize the GenAI client
    client = get_genai_client()

    # Upload section
    uploaded_files = st.file_uploader(
        label="Sube imágenes o PDFs con las facturas que quieres convertir",
        type=SUPPORTED_FILE_TYPES,
        accept_multiple_files=True,
        help="Por favor sube los archivos con facturas individuales"
    )

    generate = st.button(label="Generar 606", disabled=not uploaded_files)

    if uploaded_files and generate:
        progress_bar = st.progress(0, text="Procesando archivos...")

        # Run async pipeline
        responses_list = asyncio.run(process_files(client, uploaded_files, progress_bar))

        progress_bar.progress(1.0, text="Procesamiento completado.")
        
        # Display the results
        display_results(uploaded_files, responses_list)

if __name__ == "__main__":
    main()
