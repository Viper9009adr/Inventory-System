import pytest
from src.models import ValidationError, InventoryItem

def test_inventory_item_valid_date():
    """Test that valida data doesn't raise any errors"""
    #Using directly @staticmethod
    assert InventoryItem._validate_name("Laptop") == "Laptop"
    assert InventoryItem._validate_quantity(10) == 10
    assert InventoryItem._validate_price(99.99) == 99.99

def test_inventory_item_invalid_name():
    """Test that empty name raises ValidationError"""
    with pytest.raises(ValidationError) as excinfo:
        InventoryItem._validate_name("")
    assert "cannot be empty" in str(excinfo.value)

def test_inventory_item_negative_price():
    """Test that negative prices raise ValidationError"""
    with pytest.raises(ValidationError) as excinfo:
        InventoryItem._validate_price(-4.0)
    assert "cannot be negative" in str(excinfo.value)

def test_inventory_item_type_error():
    """"Test that wrong types raise ValidationError"""
    with pytest.raises(ValidationError) as excinfo:
        InventoryItem._validate_quantity("eight")
