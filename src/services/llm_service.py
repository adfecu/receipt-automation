"""
LLM service for processing receipt images and PDFs.
"""
import json
import asyncio
import streamlit as st
from google.genai import types
from src.models.receipt import ReceiptData
from src.prompts.extraction_prompts import prompt_image, prompt_pdf
from src.services.image_service import preprocess_image
from config import GEMINI_MODEL


async def llm_response(client, file_data, prompt, response_schema, file_name):
    """
    Sends file_data and prompt to the LLM, parses the JSON response, and returns it.
    
    Args:
        client: GenAI client instance
        file_data: File data to process
        prompt: System instruction prompt
        response_schema: Expected response schema
        file_name: Name of the file being processed
        
    Returns:
        dict or None: Parsed JSON response, or None if decoding fails
    """
    try:
        response = await client.aio.models.generate_content(
            model=GEMINI_MODEL,
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
    """
    Process multiple uploaded files (images or PDFs) concurrently.
    
    Args:
        client: GenAI client instance
        uploaded_files: List of uploaded Streamlit file objects
        progress_bar: Streamlit progress bar component
        
    Returns:
        list: List of processed results (one per file)
    """
    file_task_pairs = []
    for uploaded_file in uploaded_files:
        file_type = uploaded_file.type
        file_bytes = uploaded_file.read()

        if file_type.startswith("image"):
            # Preprocess images: crop to receipt and enhance contrast
            try:
                file_bytes = preprocess_image(file_bytes, client)
            except Exception as e:
                st.warning(f"No se pudo preprocesar {uploaded_file.name}: {e}. Usando imagen original.")
            
            part = types.Part.from_bytes(
                data=file_bytes,
                mime_type=file_type,
            )

            task = llm_response(client, part, prompt_image, list[ReceiptData], uploaded_file.name)
            file_task_pairs.append((uploaded_file, task))
        elif file_type == "application/pdf":
            part = types.Part.from_bytes(
                data=file_bytes,
                mime_type=file_type,
            )

            task = llm_response(client, part, prompt_pdf, list[ReceiptData], uploaded_file.name)
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

