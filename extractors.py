"""
extractors.py
Pulls RAW TEXT out of different file types. No AI here yet —
we're just proving we can reliably get content out of each format.
"""

import pdfplumber
import pandas as pd
import trafilatura
import requests
import pytesseract
from PIL import Image

# --- WINDOWS FIX ---
# pytesseract can't auto-find Tesseract on Windows. Point to it explicitly.
# Update this path if you installed it somewhere else.
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_website_text(url: str) -> str:
    """
    Scrape a supplier/product page and pull out the main readable content.
    trafilatura auto-strips nav bars, ads, footers — just keeps article-like text.
    """
    downloaded = trafilatura.fetch_url(url)
    if downloaded is None:
        # fallback: raw requests in case trafilatura's fetcher gets blocked
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        downloaded = resp.text

    text = trafilatura.extract(downloaded)
    if not text:
        return "[No extractable content found on this page]"
    return text


def extract_image_text(filepath: str) -> str:
    """
    OCR an image (e.g. a photographed catalog page or product label)
    and return whatever text Tesseract can read from it.
    """
    img = Image.open(filepath)
    text = pytesseract.image_to_string(img)
    return text


def extract_pdf_text(filepath: str) -> str:
    """Pull all text out of a PDF, page by page."""
    text_chunks = []
    with pdfplumber.open(filepath) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            text_chunks.append(f"--- Page {i+1} ---\n{text}")
    return "\n\n".join(text_chunks)


def extract_excel_text(filepath: str) -> str:
    """Read an Excel file and dump it as readable text (all sheets)."""
    xls = pd.ExcelFile(filepath)
    text_chunks = []
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        text_chunks.append(f"--- Sheet: {sheet_name} ---\n{df.to_string()}")
    return "\n\n".join(text_chunks)


def extract_csv_text(filepath: str) -> str:
    """Read a CSV (even a messy one) and dump it as text."""
    # on_bad_lines='skip' handles malformed rows gracefully for MVP
    df = pd.read_csv(filepath, on_bad_lines='skip', encoding_errors='ignore')
    return df.to_string()


if __name__ == "__main__":
    import sys
    filepath = sys.argv[1] if len(sys.argv) > 1 else None
    if not filepath:
        print("Usage: python extractors.py path/to/file  (or a URL)")
        sys.exit(1)

    if filepath.startswith("http"):
        print(extract_website_text(filepath))
    elif filepath.endswith(".pdf"):
        print(extract_pdf_text(filepath))
    elif filepath.endswith((".xlsx", ".xls")):
        print(extract_excel_text(filepath))
    elif filepath.endswith(".csv"):
        print(extract_csv_text(filepath))
    elif filepath.lower().endswith((".png", ".jpg", ".jpeg")):
        print(extract_image_text(filepath))
    else:
        print("Unsupported file type for this test")