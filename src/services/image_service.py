"""
Image preprocessing service for receipt images.
"""
from PIL import Image, ImageEnhance, ImageOps
import io
import json
from google.genai import types
from config import CONTRAST_ENHANCEMENT_FACTOR, BBOX_EXPANSION_FACTOR, GEMINI_MODEL_LITE


def crop_to_receipt(image, client):
    """
    Crop image to the bounding box containing the receipt using Gemini 2.0 Flash Lite.
    
    Args:
        image: PIL Image object
        client: GenAI client instance
        
    Returns:
        PIL Image: Cropped image containing the receipt
    """
    prompt = (
        "Detect the full contour of the point-of-sale paper receipt. "
        "The target area includes all text, line items, logos, and any visible QR codes "
        "associated with the receipt. Generate a bounding box that tightly encloses this "
        "entire area. The goal is to capture all receipt paper and QR codes while excluding "
        "as much of the surrounding background (e.g., table, hands, wallet) as possible. "
        "The box_2d should be [ymin, xmin, ymax, xmax] normalized to 0-1000."
    )
    
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0
    )
    
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL_LITE,
            contents=[image, prompt],
            config=config
        )
        
        width, height = image.size
        bounding_boxes = json.loads(response.text)
        
        if not bounding_boxes:
            # If no bounding boxes found, return original image
            return image
        
        # Use the first bounding box (should be the receipt)
        bounding_box = bounding_boxes[0]
        abs_y1 = int(bounding_box["box_2d"][0]/1000 * height)
        abs_x1 = int(bounding_box["box_2d"][1]/1000 * width)
        abs_y2 = int(bounding_box["box_2d"][2]/1000 * height)
        abs_x2 = int(bounding_box["box_2d"][3]/1000 * width)
        
        # Expand the bounding box by configured factor to ensure we capture everything
        box_width = abs_x2 - abs_x1
        box_height = abs_y2 - abs_y1
        expand_w = int(box_width * BBOX_EXPANSION_FACTOR)
        expand_h = int(box_height * BBOX_EXPANSION_FACTOR)
        
        x1 = max(0, abs_x1 - expand_w)
        y1 = max(0, abs_y1 - expand_h)
        x2 = min(width, abs_x2 + expand_w)
        y2 = min(height, abs_y2 + expand_h)
        
        # Crop the image
        cropped = image.crop((x1, y1, x2, y2))
        
        return cropped
        
    except Exception as e:
        # If LLM fails, return original image
        print(f"Error cropping with LLM: {e}")
        return image


def enhance_contrast(image, factor=None):
    """
    Enhance the contrast of an image by the given factor.
    
    Args:
        image: PIL Image object
        factor: Contrast enhancement factor (defaults to config value)
        
    Returns:
        PIL Image: Enhanced image
    """
    if factor is None:
        factor = CONTRAST_ENHANCEMENT_FACTOR
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)


def preprocess_image(image_bytes, client):
    """
    Complete preprocessing pipeline:
    1. Open image from bytes
    2. Fix orientation using EXIF data
    3. Crop to receipt bounding box using Gemini 2.5 Flash Lite
    4. Enhance contrast by configured factor
    
    Args:
        image_bytes: Raw image bytes
        client: GenAI client instance
        
    Returns:
        bytes: Preprocessed image as bytes
    """
    # Open image from bytes
    image = Image.open(io.BytesIO(image_bytes))
    
    # Fix orientation based on EXIF data
    image = ImageOps.exif_transpose(image)
    
    # Convert to RGB if necessary (in case it's RGBA or other format)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Step 1: Crop to receipt bounding box using LLM
    cropped_image = crop_to_receipt(image, client)
    
    # Step 2: Enhance contrast
    enhanced_image = enhance_contrast(cropped_image)
    
    # Convert back to bytes
    output_buffer = io.BytesIO()
    enhanced_image.save(output_buffer, format='JPEG')
    output_buffer.seek(0)
    
    return output_buffer.getvalue()

