import json
import asyncio
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from pydantic import BaseModel
from prompts import prompt_image, prompt_pdf

class ReceiptData(BaseModel):
    rnc: int
    ncf: str
    date: str
    subtotal: float
    itbis: float
    isc: float
    other_taxes: float
    tips: float

def main():

    # Show title and description.
    st.title("📄 606 automático")

    # Initialize the GenAI client.
    client = genai.Client()

    # Load an image and generate content.
    uploaded_files = st.file_uploader(
        label="Sube imágenes o PDFs con las facturas que quieres convertir",
        type=["jpg", "jpeg", "png", "heic", "pdf"],
        accept_multiple_files=True,
        help="Por favor sube los archivos con facturas individuales"
    )

    generate = st.button(
        label="Generar 606",
        disabled=not uploaded_files
    )

    responses_list = []

    if uploaded_files and generate:

        progress_bar = st.progress(0, text="Procesando archivos...")
        total_files = len(uploaded_files)
        for idx, uploaded_file in enumerate(uploaded_files):
            file_type = uploaded_file.type
            progress_bar.progress(
                idx / total_files,
                text=f"Procesando: {uploaded_file.name} ({idx+1}/{total_files})"
            )
            if file_type.startswith("image"):
                image = Image.open(uploaded_file)
                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=[image, prompt_image],
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": list[ReceiptData],
                    },
                )
                try:
                    # Assuming the response is a JSON string
                    json_response = json.loads(response.text)
                    responses_list.append(json_response)
                except json.JSONDecodeError:
                    st.warning(f"Could not decode JSON from image response for {uploaded_file.name}")
            elif file_type == "application/pdf":
                pdf_bytes = uploaded_file.read()
                pdf_content = types.FileData(data=pdf_bytes, mime_type="application/pdf")
                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=[pdf_content, prompt_pdf],
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": list[ReceiptData],
                    },
                )
                try:
                    # Assuming the response is a JSON string
                    json_response = json.loads(response.text)
                    responses_list.append(json_response)
                except json.JSONDecodeError:
                    st.warning(f"Could not decode JSON from PDF response for {uploaded_file.name}")
            else:
                st.warning(f"Tipo de archivo no soportado: {uploaded_file.name}")
        
        progress_bar.progress(1.0, text="Procesamiento completado.")

        # Check if there are any responses to display
        if responses_list:
            st.table(responses_list)
        else:
            st.info("No valid JSON responses were generated to display in the table.")

if __name__ == "__main__":
    main()