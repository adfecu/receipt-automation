"""
Experimental script for testing bounding box detection on receipts.

This script is for development/testing purposes only.
Make sure to set your GEMINI_API_KEY environment variable before running.
"""
import os
from google import genai
from google.genai import types
from PIL import Image, ImageDraw, ImageOps
import json

# Get API key from environment variable
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Please set GEMINI_API_KEY environment variable")

client = genai.Client(api_key=api_key)
prompt = (
    "Detect the full contour of the point-of-sale paper receipt. "
    "The target area includes all text, line items, logos, and any visible QR codes "
    "associated with the receipt. Generate a bounding box that tightly encloses this "
    "entire area. The goal is to capture all receipt paper and QR codes while excluding "
    "as much of the surrounding background (e.g., table, hands, wallet) as possible. "
    "The box_2d should be [ymin, xmin, ymax, xmax] normalized to 0-1000."
)

invoice_dir = "data/invoices2"
invoice_files = [f for f in os.listdir(invoice_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]

for invoice_file in invoice_files[1:]:
    image_path = os.path.join(invoice_dir, invoice_file)
    image = Image.open(image_path)
    image = ImageOps.exif_transpose(image)

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=[image, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0
        )
    )

    width, height = image.size
    bounding_boxes = json.loads(response.text)

    converted_bounding_boxes = []
    for bounding_box in bounding_boxes:
        abs_y1 = int(bounding_box["box_2d"][0]/1000 * height)
        abs_x1 = int(bounding_box["box_2d"][1]/1000 * width)
        abs_y2 = int(bounding_box["box_2d"][2]/1000 * height)
        abs_x2 = int(bounding_box["box_2d"][3]/1000 * width)
        # Expand box by 5% in each direction
        box_width = abs_x2 - abs_x1
        box_height = abs_y2 - abs_y1
        expand_w = int(box_width * 0.05)
        expand_h = int(box_height * 0.05)
        new_x1 = max(0, abs_x1 - expand_w)
        new_y1 = max(0, abs_y1 - expand_h)
        new_x2 = min(width, abs_x2 + expand_w)
        new_y2 = min(height, abs_y2 + expand_h)
        converted_bounding_boxes.append([new_x1, new_y1, new_x2, new_y2])

    print(f"\nImage: {invoice_file} | Size: {width}x{height}")
    print("Bounding boxes:", converted_bounding_boxes)
    draw = ImageDraw.Draw(image)
    for i, box in enumerate(converted_bounding_boxes):
        x1, y1, x2, y2 = box
        # Crop and save
        cropped = image.crop((x1, y1, x2, y2))
        cropped_dir = "data/cropped2"
        os.makedirs(cropped_dir, exist_ok=True)
        cropped_filename = f"{os.path.splitext(invoice_file)[0]}.jpg"
        cropped.save(os.path.join(cropped_dir, cropped_filename))

