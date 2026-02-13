"""
Data models for the inventory system

Models define the structure of your data and validation rules.
They don't know anything about databases or APIs - just data structure.

This is the 'M' in MVC (Model-View-Controller) pattern.
"""

from typing import Dict, Optional
from datetime import datetime

# --- Custom exception ---

class InventoryError(Exception):
    """Base exception for all inventory-related errors"""
    pass

class ValidationError(InventoryError):
    """Raised when data validation fails"""
    pass

class DatabaseError(InventoryError):
    """Raised when database operations fails"""
    pass

class ItemNotFoundError(InventoryError):
    """Raised when item cannot be found"""
    pass


# --- Data Model ---

class InventoryItem:
    """
    Represents a single inventory item

    This class:
    1. Defines what an item looks like(item_id, name , quantity, price)
    2. Validates data (name not empty, quantity >= 0, etc.)
    3. Provides conversion methods (to_dict for JSON responses)

    It does NOT:
    - Know how to save itself to a database (that's Respository's job)
    - Know about HTTP requests (that's API's job)
    - Know about business rules (that's Service's job)

    This is called " Separation of Concerns" - each class has ONE job
    """

    # Class-level constant for validation
    MAX_NAME_LENGHT = 255
    MIN_QUANTITY = 0
    MAX_QUANTITY = 1_000_000
    MIN_PRICE = 0.0
    MAX_PRICE = 1_000_000.0

    def __init__(
            self, name: str, 
            quantity: int, 
            price: float, 
            item_id: Optional[int] = None,
            created_at: Optional[str] = None,
            updated_at: Optional[str] = None
    ):
        """
        Create a new inventory item

        Args:
            name: Item name (required, 1-255 chars)
            quantity:  How many in stock (>= 0)
            price:  Price per unit (>= 0.0)
            item_id: Database ID (set by database, None for new items)
            created_at: Timestamps when created
            updated_at: Timestamps when last updated

        Raises:
            ValidationError: If any validation fails
        """
        
        self.item_id = item_id
        self.name = self._validate_name(name)
        self.quantity = self._validate_quantity(quantity)
        self.price = self._validate_price(price)
        self.created_at = created_at
        self.updated_at = updated_at 

    def to_dict(self) -> Dict:
        # Converts the object into a dictionary for API Response
        return {
            "item_id": self.item_id,
            "name": self.name,
            "quantity": self.quantity,
            "price": self.price,
            "created_at": self.created_at,
            "update_at": self.updated_at
        }

    @staticmethod
    def _validate_name(name: str) -> str:
        """
        Validate item name

        Rules:
        - Must be a string
        - Cannot be empty (after stripping whitespace)
        - Maximum 255 characters

        Returns:
            Cleaned name (whitespace stripped)

        Riases:
            ValidationError: If validation fails
        """

        if not isinstance(name, str):
            raise ValidationError(
                f"Name must be a string, got {type(name).__name__}"
            )
        
        # Remove landing/trailing whitespace
        name = name.strip()

        if not name:
            raise ValidationError(
                f"Name cannot be empty"
            )
        
        if len(name) > InventoryItem.MAX_NAME_LENGHT:
            raise ValidationError(
                f"Name too long (max {InventoryItem.MAX_NAME_LENGHT} chars)"
            )
        
        return name

    @staticmethod
    def _validate_quantity(quantity: int) -> int:
        """
        Validate quantity

        Rules:
        - Must be an integer
        - Cannot be negative
        - Cannot exceed MAX_QUANTITY

        Returns:
            Validated quantity

        Raises:
            ValidationError: if validation fails
        
        """

        if not isinstance(quantity, int):
            raise ValidationError(
                f"Quantity must be an integer, got {type(quantity).__name__}"
            )
        
        if quantity < InventoryItem.MIN_QUANTITY:
            raise ValidationError(
                f"Quantity cannot be negative, got {quantity}"
            )
        
        if quantity > InventoryItem.MAX_QUANTITY:
            raise ValidationError(
                f"Quantity too long, (max {InventoryItem.MAX_QUANTITY})"
            )
        
        return quantity

    @staticmethod
    def _validate_price(price: float) -> float:
        """
        Validate price

        Rules:
        - Must be a float
        - Cannot exceed MAX_PRICE

        Returns:
            Validated price

        Raises:
            ValidationError: if validation fails
        """

        if not isinstance(price, (float, int)):
            raise ValidationError(
                f"Price must be a number, got {type(price).__name__}"
            )
        
        if price < InventoryItem.MIN_PRICE:
            raise ValidationError(
                f"Price cannot be negative, got {price}"
            )
        
        if price > InventoryItem.MAX_PRICE:
            raise ValidationError(
                f"Price too long (max {InventoryItem.MAX_PRICE})"
            )
        
        return price

def __repr__(self) -> str:
    """String representation for debugging"""
    return(
        f"InventoryItem(id={self.item_id}, name='{self.name}', "
        f"qty={self.quantity}, price=${self.price})"
    )

def __eq__(self, other) -> bool:
    """Check if two items are equal (testing purposes)"""
    if not isinstance(other, InventoryItem):
        return False
    return (
        self.item_id == other.item_id and
        self.name == other.name and
        self.quantity == other.quantity and
        self.price == other.price
    )