# api_server - Flask API Definition (Using SQLite persistence)

from flask import Flask, jsonify, request
from typing import Dict, Any, Optional

# Importing the InventoryManager from the core file
from src.manager import InventoryManager
from src.models import InventoryItem, ValidationError

# --- Flask App Initialization ---
app = Flask(__name__)

# Initialize the Inventory Manager globally. THis also creates the inventory.db file and the inventory table when the server first starts
inventory_manager = InventoryManager()
#ml_predictor = MLPredictor()  for initializing the MLPredictor


# --- API ENDPOINT: full CRUD --- 

# R - READ ALL ITEMS
# HTTP GET request to /api/inventory will list all items
@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    #Endpoint to retrieve the entire inventory
    try:
        inventory_data = inventory_manager.get_all_items_data()
        return jsonify({
            "status": "success",
            "count": len(inventory_data),
            "inventory": inventory_data
        }), 200 # HTTP 200 OK
    except Exception as e:
        print(f"Error fetching inventory: {e}")
        return jsonify({"status": "error", "message": "Failed to retrieve inventory data"}), 500
    

# C - CREATE ITEM
# HTTP POST request to /api/item with JSON body creates a new item
@app.route('/api/item', methods=['POST'])
def add_item_api():
    #Endpoint to add a new inventory item
    try:
        # Get JSON data from the request body
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Missing JSON data in request."}), 400
        
        # Extract and validate fields
        name = data.get("name")
        quantity = data.get('quantity')
        price = data.get('price')

        if not name:
            return jsonify({"status": "error", "message": "Item name is required"}), 400
        
        if not quantity:
            return jsonify({"status": "error", "message": "Quantity is required"}), 400
        
        if not price:
            return jsonify({"status": "error", "message": "Price is required"}), 400
        
        try:
            InventoryItem._validate_name(name)
            InventoryItem._validate_quantity(quantity)
            InventoryItem._validate_price(price)

        except ValidationError as e:
            print(f"Error validation {e}")
            return jsonify({"status": "error", "message": "validation failed"})
        
        # Call the core logic layer
        new_item = inventory_manager.add_item(name, quantity, price)

        return jsonify({
            "status": "success",
            "message": f"Item '{name}' added successfully.",
            #"item": new_item.to_dict()
        }), 201 
    
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid quantity or price format."}), 400
    except Exception as e:
        print(f"Error adding item: {e}")
        return jsonify({"status": "error", "message": f"Failed to add item: {e}"}), 500
    

# U - UPDATE ITEM
# HTTP PUT request to /api/item/<id> updates item details
@app.route('/api/item/<int:item_id>', methods=['PUT'])
def update_item_api(item_id):
    # Endpoint to update an existing inventory item by Invalid
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Missing JSON data in request."}), 400
    
        # Extract and safely convert fields
        name = data.get('name')
        quantity = data.get('quantity')
        price = data.get('price')

        try:
            quantity = int(quantity) if quantity is not None else None
            price = float(price) if price is not None else None
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid quantity or price format."}), 400

        was_updated = inventory_manager.update_item(
            item_id=item_id,
            name=name,
            quantity=quantity,
            price=price
        )

        if was_updated:
            return jsonify({
                "status": "success",
                "message": f"Item ID {item_id} updated successfully."
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": f"Item ID {item_id} not found or no changes provided."
            }), 404 # HTTP 404 Not Found or HTTP 304 Not Modified

    except Exception as e:
        print(f"Error updating item: {e}")
        return jsonify({"status": "error", "message": f"Failed to update item: {e}"}), 500

# D - DELETE ITEM
# HTTP DELETE request to /api/item/<id> removes the item
@app.route('/api/item/<int:item_id>', methods=['DELETE'])
def delete_item_api(item_id):
    # Endpoint to delete an inventory item by ID.
    try:
        was_deleted = inventory_manager.delete_item(item_id)

        if was_deleted:
            return jsonify({
                "status": "success",
                "message": f"Item ID {item_id} deteled successfully."
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": f"Item ID {item_id} not found."
            }), 404
        
    except Exception as e:
        print(f"Error deleting item: {e}")
        return jsonify({{"status": "error", "message": f"Failed to delete item: {e}"}}), 500
    
@app.route('/api/item/<int:item_id>', methods=['GET'])
def get_item_api(item_id):
    # Endpoint to retrieve an inventory item by ID
    try:
        data =  inventory_manager.get_item(item_id)

        if not data:
            return jsonify({"status": "error",
                            "message":"Item not found"}), 404
        
        return jsonify({
            "status":"success",
            "inventory item": data
        }), 200


    except Exception as e:
        return jsonify({"status":"error", "message":f"Failed to retrieve item: {e}"}), 404


