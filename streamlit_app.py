import json
import asyncio
import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel
from utils.prompts import prompt_image, prompt_pdf
import pandas as pd
from utils.dgii import consulta_rnc  # make sure this is the correct import


class ReceiptData(BaseModel):
    rnc_vendor: int
    ncf: str
    date: str
    subtotal: float
    itbis: float
    isc: float
    # other_taxes: float
    tips: float


# ---- Cache the DGII query ----
@st.cache_data(show_spinner=False)
def cached_consulta_rnc(rnc: int):
    """Cached wrapper for consulta_rnc to avoid repeated API calls."""
    try:
        return consulta_rnc(rnc)
    except Exception:
        return None


def highlight_invalid_rnc(val):
    """Return red background if RNC is invalid (consulta_rnc returns None)."""
    try:
        if not val:  # empty or NaN
            return "background-color: red; color: white;"
        result = cached_consulta_rnc(int(val))
        if not result:  # DGII didn’t return data
            return "background-color: red; color: white;"
    except Exception:
        return "background-color: red; color: white;"
    return ""


# ---------- ASYNC LLM CALL ----------
async def llm_response(client, file_data, prompt, response_schema, file_name):
    """
    Sends file_data and prompt to the LLM, parses the JSON response, and returns it.
    Returns None if JSON decoding fails.
    """
    try:
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=[file_data],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
                system_instruction=prompt,
                temperature=0
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
            pdf_content = types.FileData(
                data=pdf_bytes, 
                mime_type="application/pdf"
            )
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

        valid_responses = [r for r in responses_list if r and not isinstance(r, Exception)]
        # Flatten the list of lists (if each response is a list of dicts)
        flattened = []
        for item in valid_responses:
            flattened.extend(item)
        if flattened:
            df = pd.DataFrame(flattened)

            # Apply style only to the rnc_vendor column
            styled_df = df.style.map(highlight_invalid_rnc, subset=["rnc_vendor"])

            st.dataframe(styled_df)
        else:
            st.info("No valid JSON responses were generated to display in the table.")


if __name__ == "__main__":
    main()
