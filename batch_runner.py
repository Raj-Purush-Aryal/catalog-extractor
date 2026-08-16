"""
batch_runner.py
Processes an entire folder of mixed files (PDF, CSV, XLSX, images)
and combines everything into ONE clean output spreadsheet.
"""

import os
from extractors import (
    extract_pdf_text, extract_excel_text, extract_csv_text,
    extract_image_text, extract_website_text
)
from structurer import structure_text
from exporter import export_to_excel
from schema import Product


def get_raw_text(filepath: str) -> str | None:
    """Route a file to the right extractor based on its extension."""
    ext = filepath.lower().split(".")[-1]
    try:
        if ext == "pdf":
            return extract_pdf_text(filepath)
        elif ext in ("xlsx", "xls"):
            return extract_excel_text(filepath)
        elif ext == "csv":
            return extract_csv_text(filepath)
        elif ext in ("png", "jpg", "jpeg"):
            return extract_image_text(filepath)
        else:
            print(f"  Skipping unsupported file: {filepath}")
            return None
    except Exception as e:
        print(f" Failed to extract from {filepath}: {e}")
        return None


def run_batch(folder_path: str, output_path: str = "combined_catalog.xlsx"):
    """Process every supported file in a folder and export one combined spreadsheet."""
    all_products: list[Product] = []
    files = [f for f in os.listdir(folder_path) if not f.startswith(".")]

    print(f" Found {len(files)} file(s) in {folder_path}\n")

    for filename in files:
        filepath = os.path.join(folder_path, filename)
        if not os.path.isfile(filepath):
            continue

        print(f"--- Processing: {filename} ---")
        raw_text = get_raw_text(filepath)

        if not raw_text or not raw_text.strip():
            print(f"  No text extracted from {filename}, skipping.\n")
            continue

        try:
            products = structure_text(raw_text)
            print(f" Got {len(products)} product(s) from {filename}\n")
            all_products.extend(products)
        except Exception as e:
            print(f" Structuring failed for {filename}: {e}\n")
            continue

    print(f"\n Total products collected: {len(all_products)}")

    if all_products:
        export_to_excel(all_products, output_path)
    else:
        print(" No products extracted from any file — nothing to export.")


if __name__ == "__main__":
    import sys
    folder = sys.argv[1] if len(sys.argv) > 1 else "samples"
    run_batch(folder)