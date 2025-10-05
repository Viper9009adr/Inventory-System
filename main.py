class InventoryItem:
    """
    Blueprint for a single item (the data structure)
    """
    def __init__(self, item_id: str, name: str, quantity: int, price: float):
        #Attributes prefixed with self. are instance variables
        self.item_id = item_id
        self.name = name
        self.quantity = quantity
        self.price = price

    def __str__(self):
        """Defines how the object prints to the console"""
        return(
            f"ID: {self.item_id:<10} | Name: {self.name:<25} | "
            f"Qty: {self.quantity:<5} | Price: ${self.price:.2f}"
        )

class InventoryManager:
    """
    The controller for the inventory (the business logic).
    Manage the storage, retrieval, and modification of items.
    """
    def __init__(self):
        # This is the single, central dictionary that holds all inventory items
        # Key : item_id(str)
        # Value : InventoryItem object
        self.inventory_storage = {}
        print("Inventory Manager Initialized.")


# --- Example Usage (How we will test the class later) ---
# manager = InventoryManager()
# new_item = InventoryItem("AX-001", "Axe Head", 5, 45.00)
# manager.inventory_storage[new_item.item_id] = new_item
# print(manager.inventory_storage["AX-001"])


    def add_item(self, item_id: str, name: str, quantity: int, price: float):
        if item_id in self.inventory_storage:
            return f"{name} Already in Inventory"
        else:
            item = InventoryItem(item_id, name, quantity, price)
            self.inventory_storage[item_id] = item
            return f"{name} added correctly"


    def remove_item(self, item_id: str,):
        if item_id in self.inventory_storage:
            item_to_remove = self.inventory_storage[item_id]
            item_name = item_to_remove.name
            self.inventory_storage.pop(item_id)
            return f"{item_name} removed successfully"
        else:
            return f"{item_id} doesn't exist"
        



manager = InventoryManager()

# Add items
print(manager.add_item("S-101", "Small Screwdriver", 50, 4.99))
print(manager.add_item("H-500", "Hammer, 20oz Steel", 15, 18.50))

# Try to add a duplicate (should fail)
print(manager.add_item("S-101", "Duplicate Screwdriver", 5, 1.00)) 

# Remove an existing item
print(manager.remove_item("H-500"))

# Try to remove a non-existent item (should fail)
print(manager.remove_item("X-999"))
