"""
Inventory Manager handler
"""

import sqlite3
from typing import Dict, List, Any, Optional

from src.models import InventoryItem
from src.database import DatabaseSession

class InventoryManager:
    def __init__(self, db_name: str = 'inventory.db'):
        self.db_name = db_name
        self._init_db()
    
    def _init_db(self):
        """Creates the inventory table if it does not exist."""
        with DatabaseSession(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    item_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL
                    )
            ''')
            print(f"Sqlite database initialized: {self.db_name}")

    # C - CREATE (Add Item)
    def add_item(self, name: str, quantity: int, price: float) -> InventoryItem:
        """Adds a new item to the database using an INSERT SQL Query."""
        with DatabaseSession(self.db_name) as conn:
            cursor = conn.cursor()

            # INSERT Statement: Always use '?' placeholders to prevent SQL Injection attacks.
            cursor.execute(
            "INSERT INTO inventory (name, quantity, price) VALUES (?, ?, ?)",
            (name, quantity, price)
            )
            # Retrieve the ID that SQLite just generated
            new_id = cursor.lastrowid

            print(f"Added item '{name}' with ID {new_id} to SQLite.")
            return InventoryItem(name, quantity, price, item_id=new_id)
    
    # R - READ (Get All Items)
    def get_all_items_data(self) -> List[Dict]:
        with DatabaseSession(self.db_name) as conn:
            
            cursor = conn.cursor()

            cursor.execute("SELECT item_id, name, quantity, price FROM inventory")
            results = cursor.fetchall()

            #Convert the results into a standard list of dictionaries
            inventory_list = [dict(row) for row in results]
            return inventory_list
    
    # U - UPDATE (Update Item)
    def update_item(self, item_id: int, name: Optional[str] = None, quantity: Optional[int] = None, price: Optional[float] = None) -> bool:
        """Updates item fields using an UPDATE SQL query"""
        with DatabaseSession(self.db_name) as conn:
            cursor = conn.cursor()

            updates = []
            params = []

            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if quantity is not None:
                updates.append("quantity = ?")
                params.append(quantity)
            if price is not None:
                updates.append("price = ?")
                params.append(price)

            if not updates:
                return False # Nothing to update
            
            # Build the full SQL command dynamically
            set_clause = ", ".join(updates)
            sql_command = f"UPDATE inventory SET {set_clause} WHERE item_id = ?"
            params.append(item_id)
            cursor.execute(sql_command, tuple(params))
            

            # Check if exactly one row was updated
            return cursor.rowcount > 0
    

    # D - DELETE (Remove Item)
    def delete_item(self, item_id: int) -> bool:
        """Deletes an item by ID using a DELETE SQL query."""
        with DatabaseSession(self.db_name) as conn:
            cursor = conn.cursor()

            # DELETE Statement
            cursor.execute("DELETE FROM inventory WHERE item_id = ?", (item_id,))
            
            # Check if the deletion was successful
            return cursor.rowcount > 0
    

    def get_item(self, item_id):
        with DatabaseSession(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM inventory WHERE item_id = ?',(item_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)            
            return None


    
# NOTE: The database connection is done through the context manager created in the DatabaseSession class, which ensures safely closing it.
