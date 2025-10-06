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
            f"| ID: {self.item_id:<10}| Name: {self.name:<25}| Qty: {self.quantity:<5}| Price: ${self.price:.2f}"
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
            item = InventoryItem(item_id, name, quantity, price)
            self.inventory_storage[item_id] = item
            return f"{name} added correctly"
        
    def check_item(self, item_id):
        if item_id in self.inventory_storage:
            return True


    def remove_item(self, item_id: str,):
        if item_id in self.inventory_storage:
            item_name = self.inventory_storage.pop(item_id)
            return f"{item_name.name} removed successfully"
        else:
            return f"{item_id} doesn't exist"
        

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
    
def print_help():
    print("\n--- Available Commands ---")
    print("add:     Add a new item(requires ID, Name, Qty, Price).")
    print("remove:  Remove an item by ID.")
    print("view:    Display all item in inventory.")
    print("exit:    Quit the program.")
    print("-"*28)

def run_cli():

    manager = InventoryManager()

    print_help()

    while True:
            try:
                command = input("Enter command or 'help': ").lower().strip()

                if command == "exit":
                    print("Exciting Inventory System, Have a Nice Day!")
                    break

                #elif command == "perra":     
                    #print("Tu vieja, puto!")
                
                elif command == "help":
                    print_help()

                elif command == "view":
                    print(manager.view_inventory())
                
                elif command == "remove":
                    item_id = input("Enter ID of imtem to remove: ").strip()
                    print(manager.remove_item(item_id))

                elif command == "add":
                    try:
                        item_id = input("Enter ID: ").strip()
                        if manager.check_item(item_id) == True:
                            print(f"{item_id} Already in Inventory")
                            continue

                        
                        name = input("Enter Name: ").strip()
                        quantity = int(input("Enter Quantity: "))
                        price = float(input("Enter Price: "))

                        if quantity < 0 or price < 0:
                            print("ERROR: Quantity and Price cannot be negative")
                            continue

                        print(manager.add_item(item_id, name, quantity, price))
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

                


