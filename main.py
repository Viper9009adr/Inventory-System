import sqlite3
from typing import Dict, List, Any, Optional


# InventoryItem Class
# The Item class is now simplified, letting the database handle the ID generation
class InventoryItem:
    """
    Blueprint for a single item (the data structure)
    """
    def __init__(self, name: str, quantity: int, price: float, item_id: Optional[int] = None, ):
        self.item_id = item_id
        self.name = name
        self.quantity = quantity
        self.price = price

    def to_dict(self) -> Dict:
        # Converts the object into a dictionary for API Response
        return {
            "item_id": self.item_id,
            "name": self.name,
            "quantity": self.quantity,
            "price": self.price
        }

class InventoryManager:
    """Manages the collection of inventory items using SQLite for persistence."""
    def __init__(self, db_name: str = 'inventory.db'):
        # The database file name
        self.db_name = db_name
        self.conn = None
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Establishes or returns the database connection"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_name)
            # This line makes results come back as dictionaries (squlite3.Row objects) instead of tuples.
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def _init_db(self):
        """Creates the inventory table if it does not exist."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            # CRUCIAL SQL: Defining the schema.
            # INTEGER PRIMARY KEY automatically handles auto-incrementing ID.
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    item_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL
                )
            ''')
            conn.commit()
            print(f"SQLite database initialized: {self.db_name}")
        except sqlite3.Error as e:
            print(f"Database Initialization Error: {e}")

    # --- CRUD Operations ---

    # C - CREATE (Add Item)
    def add_item(self, name: str, quantity: int, price: float) -> InventoryItem:
        """Adds a new item to the database using an INSERT SQL Query."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # INSERT Statement: Always use '?' placeholders to prevent SQL Injection attacks.
        cursor.execute(
            "INSERT INTO inventory (name, quantity, price) VALUES (?, ?, ?)",
            (name, quantity, price)
        )
        # Retrieve the ID that SQLite just generated
        new_id = cursor.lastrowid
        conn.commit()

        print(f"Added item '{name}' with ID {new_id} to SQLite.")
        return InventoryItem(name, quantity, price, item_id=new_id)
    
    # R - READ (Get All Items)
    def get_all_items_data(self) -> List[Dict]:
        """Retrieves all items using a SELECT SQL query."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT item_id, name, quantity, price FROM inventory")
        results = cursor.fetchall()

        #Convert the results into a standard list of dictionaries
        inventory_list = [Dict(row) for row in results]
        return inventory_list
    
    # U - UPDATE (Update Item)
    def update_item(self, item_id: int, name: Optional[str] = None, quantity: Optional[int] = None, price: Optional[float] = None) -> bool:
        """Updates item fields using an UPDATE SQL query"""
        conn = self.get_connection()
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
        conn.commit()

        # Check if exactly one row was updated
        return cursor.rowcount > 0
    

    # D - DELETE (Remove Item)
    def delete_item(self, item_id: int) -> bool:
        """Deletes an item by ID using a DELETE SQL query."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # DELETE Statement
        cursor.execute("DELETE FROM inventory WHERE item_id = ?", {item_id})
        conn.commit()

        # Check if the deletion was successful
        return cursor.rowcount > 0
    
# NOTE: The database connection is kept open until the server explicitly terminates.



