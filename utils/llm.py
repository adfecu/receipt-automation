import json
import asyncio
from pydantic import BaseModel
import streamlit as st
from google.genai import types
from utils.prompts import prompt_image, prompt_pdf

class ReceiptData(BaseModel):
    rnc_vendor: int
    ncf: str
    date: str
    subtotal: float
    itbis: float
    isc: float
    # other_taxes: float
    tips: float

async def llm_response(client, file_data, prompt, response_schema, file_name):
    """
    Sends file_data and prompt to the LLM, parses the JSON response, and returns it.
    Returns None if JSON decoding fails.
    """
    try:
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=[file_data],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
                system_instruction=prompt,
                temperature=0,
                thinking_config=types.ThinkingConfig(thinking_budget=0)
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

async def process_files(client, uploaded_files, progress_bar):
    file_task_pairs = []
    for uploaded_file in uploaded_files:
        file_type = uploaded_file.type
        if file_type.startswith("image"):
            image_bytes = uploaded_file.read()
            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type=uploaded_file.type
            )
            task = llm_response(client, image_part, prompt_image, list[ReceiptData], uploaded_file.name)
            file_task_pairs.append((uploaded_file, task))
        elif file_type == "application/pdf":
            pdf_bytes = uploaded_file.read()
            pdf_content = types.FileData(
                data=pdf_bytes,
                mime_type="application/pdf"
            )
            task = llm_response(client, pdf_content, prompt_pdf, list[ReceiptData], uploaded_file.name)
            file_task_pairs.append((uploaded_file, task))
        else:
            st.warning(f"Tipo de archivo no soportado: {uploaded_file.name}")

    results = [None] * len(file_task_pairs)
    total_files = len(file_task_pairs)

    # Run all tasks concurrently and preserve order
    coros = [task for (_, task) in file_task_pairs]
    completed = await asyncio.gather(*coros)
    for idx, (uploaded_file, _) in enumerate(file_task_pairs):
        progress_bar.progress((idx + 1) / total_files, text=f"Procesando archivo {idx + 1}/{total_files}")
        results[idx] = completed[idx]

    return results
