import json
import asyncio
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from pydantic import BaseModel
from utils.prompts import prompt_image, prompt_pdf


class ReceiptData(BaseModel):
    rnc: int
    ncf: str
    date: str
    subtotal: float
    itbis: float
    isc: float
    other_taxes: float
    tips: float


# ---------- ASYNC LLM CALL ----------
async def llm_response(client, file_data, prompt, response_schema, file_name):
    """
    Sends file_data and prompt to the LLM, parses the JSON response, and returns it.
    Returns None if JSON decoding fails.
    """
    try:
        response = await client.aio.models.generate_content(
            model="gemini-2.0-flash-lite-001",
            contents=[file_data],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
                system_instruction=prompt
            ),
        )
        json_response = json.loads(response.text)
        return json_response
    except json.JSONDecodeError:
        st.warning(f"Could not decode JSON from response for {file_name}")
        return None
    except Exception as e:
        st.error(f"Error processing {file_name}: {e}")
        return None


# ---------- PROCESS FILES IN PARALLEL ----------
async def process_files(client, uploaded_files, progress_bar):
    tasks = []
    for uploaded_file in uploaded_files:
        file_type = uploaded_file.type
        if file_type.startswith("image"):
            image_bytes = uploaded_file.read()
            image_part = types.Part.from_bytes(
                data=image_bytes, 
                mime_type=uploaded_file.type
            )
            tasks.append(
                llm_response(client, image_part, prompt_image, list[ReceiptData], uploaded_file.name)
            )
        elif file_type == "application/pdf":
            pdf_bytes = uploaded_file.read()
            pdf_content = types.FileData(data=pdf_bytes, mime_type="application/pdf")
            tasks.append(
                llm_response(client, pdf_content, prompt_pdf, list[ReceiptData], uploaded_file.name)
            )
        else:
            st.warning(f"Tipo de archivo no soportado: {uploaded_file.name}")

    results = []
    total_files = len(tasks)

    # As tasks finish, update progress
    for idx, coro in enumerate(asyncio.as_completed(tasks), start=1):
        result = await coro
        results.append(result)
        progress_bar.progress(idx / total_files, text=f"Procesando archivo {idx}/{total_files}")

    return results


# ---------- STREAMLIT APP ----------
def main():
    st.markdown("<h1 style='text-align: center;'>📄 606 automático</h1>", unsafe_allow_html=True)

    # Initialize the GenAI client
    client = genai.Client()

    # Upload section
    uploaded_files = st.file_uploader(
        label="Sube imágenes o PDFs con las facturas que quieres convertir",
        type=["jpg", "jpeg", "png", "heic", "pdf"],
        accept_multiple_files=True,
        help="Por favor sube los archivos con facturas individuales"
    )

    generate = st.button(label="Generar 606", disabled=not uploaded_files)

    if uploaded_files and generate:
        progress_bar = st.progress(0, text="Procesando archivos...")

        # Run async pipeline
        responses_list = asyncio.run(process_files(client, uploaded_files, progress_bar))

        progress_bar.progress(1.0, text="Procesamiento completado.")

        valid_responses = [r for r in responses_list if r and not isinstance(r, Exception)]
        if valid_responses:
            st.table(valid_responses)
        else:
            st.info("No valid JSON responses were generated to display in the table.")


if __name__ == "__main__":
    main()
