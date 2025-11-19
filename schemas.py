"""
Database Schemas for Readopt (Used Books Marketplace)

Each Pydantic model represents a MongoDB collection.
Collection name is the lowercase of the class name, e.g.:
- Listing -> "listing"
- User -> "user"
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal


class User(BaseModel):
    """
    Users collection schema
    Collection name: "user"
    """
    name: str = Field(..., description="Full name of the user")
    email: EmailStr = Field(..., description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone number")
    location: Optional[str] = Field(None, description="City or area")
    is_active: bool = Field(True, description="Whether user is active")


class Listing(BaseModel):
    """
    Book listings created by users
    Collection name: "listing"
    """
    title: str = Field(..., description="Book title")
    author: str = Field(..., description="Book author")
    price: float = Field(..., ge=0, description="Price in USD")
    condition: Literal["new", "like new", "good", "fair", "poor"] = Field(
        "good", description="Book condition"
    )
    description: Optional[str] = Field(None, description="Additional details")
    image_url: Optional[str] = Field(None, description="Cover image URL")
    seller_name: str = Field(..., description="Seller's name")
    seller_email: EmailStr = Field(..., description="Seller's email for contact")
    location: Optional[str] = Field(None, description="Pickup location or area")
    category: Optional[str] = Field(None, description="Genre or category")
