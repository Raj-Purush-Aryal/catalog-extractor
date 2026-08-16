"""
exporter.py
Converts structured Product objects into a clean Excel file
ready for Amazon/Shopify/marketplace upload.
"""

import pandas as pd
from datetime import datetime
from schema import Product


def products_to_dataframe(products: list[Product]) -> pd.DataFrame:
    """Convert Product objects into a flat pandas DataFrame."""
    rows = []
    for p in products:
        row = p.model_dump()
        # Features is a list — join into a single readable string for spreadsheet cells
        if row.get("features"):
            row["features"] = "; ".join(row["features"])
        rows.append(row)

    df = pd.DataFrame(rows)

    # Nice column order + friendly headers for a marketplace-ready sheet
    column_order = [
        "sku", "title", "brand", "category", "price", "color",
        "material", "dimensions", "upc", "features", "warranty", "shipping_info"
    ]
    column_order = [c for c in column_order if c in df.columns]
    df = df[column_order]

    df.columns = [
        "SKU", "Title", "Brand", "Category", "Price", "Color",
        "Material", "Dimensions", "UPC", "Features", "Warranty", "Shipping Info"
    ][:len(df.columns)]

    return df


def export_to_excel(products: list[Product], output_path: str = None) -> str:
    """Save products to a formatted Excel file. Returns the file path."""
    if not products:
        print("⚠️ No products to export.")
        return None

    df = products_to_dataframe(products)

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"output_catalog_{timestamp}.xlsx"

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Catalog")

        # Auto-width columns so it's readable, not a wall of tiny cells
        worksheet = writer.sheets["Catalog"]
        for i, col in enumerate(df.columns):
            max_len = max(df[col].fillna("").astype(str).map(len).max(), len(col)) + 2
            col_letter = worksheet.cell(row=1, column=i + 1).column_letter
            worksheet.column_dimensions[col_letter].width = min(max_len, 50)

    print(f"✅ Exported {len(products)} product(s) to: {output_path}")
    return output_path


if __name__ == "__main__":
    # Quick standalone test with fake data
    test_products = [
        Product(sku="TEST-001", title="Test Product", brand="TestBrand",
                price="$9.99", features=["Feature A", "Feature B"])
    ]
    export_to_excel(test_products, "test_output.xlsx")