"""
structurer.py
Takes raw messy text (from ANY source — PDF, CSV, website, OCR)
and asks Gemini to extract structured product data matching our schema.
"""

import os
import json
from google import genai
from dotenv import load_dotenv
from schema import Product

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-3.1-flash-lite"

EXTRACTION_PROMPT = """You are a data extraction engine for an e-commerce catalog system.

Given the RAW TEXT below (which may come from a PDF, spreadsheet, website, or OCR scan,
and may contain noise, formatting artifacts, or irrelevant text), extract ALL distinct
products mentioned and return ONLY a JSON array, no other text, no markdown fences.

Each product object must have exactly these fields (use null if not found/not applicable):
sku, title, brand, category, price, color, material, dimensions, upc, features (array of strings), warranty, shipping_info

Rules:
- If multiple products appear in the text, return one object per product.
- Ignore unrelated noise (navigation menus, unrelated "recently viewed" items, UI text, timestamps).
- Do not invent data that isn't present in the text.
- Price should include currency symbol if shown.

RAW TEXT:
{raw_text}
"""


def structure_text(raw_text: str) -> list[Product]:
    """Send raw text to Gemini, get back a list of validated Product objects."""
    prompt = EXTRACTION_PROMPT.format(raw_text=raw_text)

    print(f"📤 Sending {len(raw_text)} characters to Gemini...")

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    print("📥 Raw response object:", response)

    if not response.candidates:
        print("⚠️ No candidates returned — likely blocked or empty.")
        return []

    text = response.text
    if not text:
        print("⚠️ response.text is empty.")
        print("Finish reason:", response.candidates[0].finish_reason)
        return []

    raw = text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    print("📄 Cleaned text from Gemini:\n", raw[:500])

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print("⚠️ Could not parse Gemini's response as JSON:")
        print(raw)
        raise e

    products = [Product(**item) for item in data]
    return products


if __name__ == "__main__":
    import sys
    from extractors import extract_csv_text, extract_pdf_text, extract_website_text, extract_image_text, extract_excel_text

    filepath = sys.argv[1] if len(sys.argv) > 1 else None
    if not filepath:
        print("Usage: python structurer.py path/to/file (or URL)")
        sys.exit(1)

    if filepath.startswith("http"):
        raw = extract_website_text(filepath)
    elif filepath.endswith(".pdf"):
        raw = extract_pdf_text(filepath)
    elif filepath.endswith((".xlsx", ".xls")):
        raw = extract_excel_text(filepath)
    elif filepath.endswith(".csv"):
        raw = extract_csv_text(filepath)
    elif filepath.lower().endswith((".png", ".jpg", ".jpeg")):
        raw = extract_image_text(filepath)
    else:
        print("Unsupported file type")
        sys.exit(1)

    print(f"🔍 Extracted raw text length: {len(raw)} characters")
    print("Preview:", raw[:200])

    products = structure_text(raw)
    print(f"\n✅ Extracted {len(products)} product(s):\n")
    for p in products:
        print(p.model_dump_json(indent=2))