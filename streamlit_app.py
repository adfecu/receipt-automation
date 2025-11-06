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
        help="Por favor sube los archivos con facturas individuales. Máximo 10 archivos por vez."
    )

    # Validate file count limit (10 files max)
    MAX_FILES = 10
    file_count_exceeded = uploaded_files and len(uploaded_files) > MAX_FILES
    
    if file_count_exceeded:
        st.error(f"⚠️ Has subido {len(uploaded_files)} archivos. El límite es de {MAX_FILES} archivos a la vez debido a las limitaciones de la aplicación.")
        st.info("Por favor, elimina algunos archivos y vuelve a intentar.")

    generate = st.button(label="Generar 606", disabled=not uploaded_files or file_count_exceeded)

    if uploaded_files and generate and not file_count_exceeded:
        # Limit to first 10 files if somehow more are selected
        files_to_process = uploaded_files[:MAX_FILES] if len(uploaded_files) > MAX_FILES else uploaded_files
        
        progress_bar = st.progress(0, text="Procesando archivos...")

        # Run async pipeline
        responses_list = asyncio.run(process_files(client, files_to_process, progress_bar))

        progress_bar.progress(1.0, text="Procesamiento completado.")
        
        # Display the results
        display_results(files_to_process, responses_list)

if __name__ == "__main__":
    main()
