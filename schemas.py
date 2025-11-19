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

from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import Optional, List

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: Optional[str] = Field(None, description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    images: List[HttpUrl] = Field(default_factory=list, description="Image URLs")
    in_stock: bool = Field(True, description="Whether product is in stock")
    featured: bool = Field(False, description="Feature on homepage")

class DistributorApplication(BaseModel):
    """
    Distributors collection schema
    Collection name: "distributorapplication" -> use as lead capture for distributor partners
    """
    name: str = Field(..., description="Applicant full name")
    email: EmailStr = Field(..., description="Contact email")
    company: Optional[str] = Field(None, description="Company or brand")
    website: Optional[HttpUrl] = Field(None, description="Company website")
    location: Optional[str] = Field(None, description="City/Country")
    message: Optional[str] = Field(None, description="Additional details")

class OrderItem(BaseModel):
    product_id: str
    title: str
    quantity: int = Field(..., ge=1)
    price: float = Field(..., ge=0)
    image: Optional[HttpUrl] = None

class CheckoutRequest(BaseModel):
    items: List[OrderItem]
    customer_name: str
    customer_email: EmailStr
    address: str
    city: str
    country: str

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
