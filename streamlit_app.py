import asyncio
import streamlit as st
from google import genai
from utils.result import display_results
from utils.llm import process_files


# ---------- STREAMLIT APP ----------
def main():
    st.markdown("<h1 style='text-align: center;'>📄 606 automático</h1>", unsafe_allow_html=True)

    # Initialize the GenAI client
    client = genai.Client()

    # Upload section
    uploaded_files = st.file_uploader(
        label="Sube imágenes o PDFs con las facturas que quieres convertir",
        type=["jpg", "jpeg", "pdf"],
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
