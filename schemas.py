"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional

# Example schemas (you can keep or extend these)

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Store(BaseModel):
    """
    UMKM stores collection schema
    Collection name: "store"
    """
    name: str = Field(..., description="Store name")
    owner: Optional[str] = Field(None, description="Owner name")
    city: Optional[str] = Field(None, description="City / Location")
    logo_url: Optional[str] = Field(None, description="Logo image URL")
    description: Optional[str] = Field(None, description="Short store description")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in local currency")
    category: Optional[str] = Field(None, description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")
    image_url: Optional[str] = Field(None, description="Image URL")
    store_id: str = Field(..., description="Referenced store ID as string")

# Add your own schemas here if needed
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
