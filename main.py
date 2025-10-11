import json
import os
from typing import Dict, List, Any



class InventoryItem:
    """
    Blueprint for a single item (the data structure)
    """
    def __init__(self, item_id: int, name: str, quantity: int, price: float):
        #Attributes prefixed with self. are instance variables
        self.item_id = item_id
        self.name = name
        self.quantity = quantity
        self.price = price

    def __str__(self):
        """Defines how the object prints to the console"""
        return(
            f"| ID: {self.item_id:<10}| Name: {self.name:<25}| Qty: {self.quantity:<5}| Price: ${self.price:.2f}"
        )
    
    def to_dict(self) -> Dict:
        return {
            "item_id": self.item_id,
            "name": self.name,
            "quantity": self.quantity,
            "price": self.price
        }

class InventoryManager:
    """
    The controller for the inventory (the business logic).
    Manage the storage, retrieval, and modification of items.
    """
    def __init__(self):
        # This is the single, central dictionary that holds all inventory items
        # Key : item_id(str)
        # Value : InventoryItem object
        self.inventory_storage: Dict[int, InventoryItem] = {}
        self._next_id = 1
        


# --- Example Usage (How we will test the class later) ---
# manager = InventoryManager()
# new_item = InventoryItem("AX-001", "Axe Head", 5, 45.00)
# manager.inventory_storage[new_item.item_id] = new_item
# print(manager.inventory_storage["AX-001"])
 

    def add_item(self, item_id: int, name: str, quantity: int, price: float):
            item = InventoryItem(self._next_id, name, quantity, price)
            self.inventory_storage[self._next_id] = item
            self._next_id += 1
            return f"{name} added correctly with ID {self._next_id - 1}"
        
    def check_item(self, item_id: int) -> bool:
        return item_id in self.inventory_storage


    def remove_item(self, item_id: int):
        if item_id in self.inventory_storage:
            item_name = self.inventory_storage.pop(item_id)
            return f"{item_name.name} removed successfully"
        else:
            return f"Item with ID {item_id} doesn't exist"
        

    def view_inventory(self):
        if not self.inventory_storage:
            return "Inventory is empty"
        

        output = [
            "\n" + "="*80,
            f"| {"ID":<10}    | {"Name":<25}      | {"Quantity":<8}  | {"Price":<10} ",
            "-"*80
        ]
  

        for item in self.inventory_storage.values():
            output.append(str(item))

        output.append("="*80 + "\n")

        return "\n".join(output)
    

    def save_inventory(self, filepath: str = 'inventory_data.json'):
        inventory_data = []
        for item in self.inventory_storage.values():
            inventory_data.append(item.to_dict())

        try:
            with open(filepath, "w") as f:
                json.dump(inventory_data, f, indent=4)
            print(f"Inventory saved succesfully to {filepath}.")
        except IOError as e:
            print(f"Error saving inventory: {e}")

    def load_inventory(self, filepath: str = "inventory_data.json"):
        if not os.path.exists(filepath):
            print(f"No previous inventory file found. Starting fresh.")
            return
        
        try:
            with open(filepath, "r") as f:
                data: List[Dict[int, Any]] = json.load(f)

            if not data:
                print("Inventory is empty.")
                return
            
            max_id = 0
            for item_dict in data:
                item_id_int = int(item_dict['item_id'])

                item = InventoryItem(
                    item_id=item_id_int,
                    name=item_dict['name'],
                    quantity=item_dict['quantity'],
                    price=item_dict['price']
                )
                self.inventory_storage[item_id_int] = item
                if item_id_int > max_id:
                    max_id = item_id_int

             
            self._next_id = max_id + 1
            print(f"Inventory loaded successfully from {filepath}. Next ID will be {self._next_id}.")

        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading inventory from {filepath}: {e}")



    
def print_help():
    print("\n--- Available Commands ---")
    print("add:     Add a new item(requires ID, Name, Qty, Price).")
    print("remove:  Remove an item by ID.")
    print("view:    Display all item in inventory.")
    print("exit:    Quit the program.")
    print("-"*28)

def run_cli():

    manager = InventoryManager()

    manager.load_inventory()

    print_help()

    while True:
            try:
                command = input("Enter command or 'help': ").lower().strip()

                if command == "exit":
                    manager.save_inventory()
                    print("Exciting Inventory System, Have a Nice Day!")
                    break

                #elif command == "perra":     
                    #print("Tu vieja, puto!")
                
                elif command == "help":
                    print_help()

                elif command == "view":
                    print(manager.view_inventory())
                
                elif command == "remove":
                    try:
                        item_id = int(input("Enter ID of item to remove: ").strip())
                        print(manager.remove_item(item_id))
                    except ValueError:
                        print("Error: ID must be a number")

                elif command == "add":
                    try:
                        name = input("Enter Name: ").strip()
                        quantity = int(input("Enter Quantity: "))
                        price = float(input("Enter Price: "))

                        if quantity < 0 or price < 0:
                            print("ERROR: Quantity and Price cannot be negative")
                            continue

                        print(manager.add_item(0, name, quantity, price))  # 0 is a placeholder since ID is auto-generated
                    except ValueError:
                        print("Error: Quantity must be a whole number and Price must be a decimal number.")
                    except Exception as e:
                        print(f"An error occurred during addition: {e}")

                else:
                    print(f"Unknown command: '{command}'. Type 'help' for options.")

            except EOFError:
                print("\nExiting Inventory System, Have a Nice Day!")
                break

            except Exception as e:
                print(f"An error occurred during addition: {e}")


if __name__ == "__main__":
    run_cli()

                


