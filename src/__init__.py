"""
Inventory Management System

A production-ready REST API for inventory management with:
- CRUD operations
- Pagination and filetering
- Comprehensive error and handling
- Full test coverage
"""

__version__ = "1.0.0"
__author__ = "Viper9009adr"

from src.models import InventoryItem
from src.manager import InventoryManager
from src.database import DatabaseSession
from src.api import app


__all__ = [
    'InventoryItem',
    'InventoryManager',
    'DatabaseSession',
    'app'
]