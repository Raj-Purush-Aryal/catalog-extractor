"""
schema.py
Defines the exact structure we want every product to end up in,
no matter what messy format it started as.
Pydantic will validate Gemini's output against this automatically.
"""

from pydantic import BaseModel
from typing import Optional, List


class Product(BaseModel):
    sku: Optional[str] = None
    title: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    price: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    dimensions: Optional[str] = None
    upc: Optional[str] = None
    features: Optional[List[str]] = None
    warranty: Optional[str] = None
    shipping_info: Optional[str] = None

    class Config:
        extra = "ignore"  # if Gemini adds extra fields, don't crash