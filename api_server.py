# api_server - Flask API Definition (Using SQLite persistence)

from flask import Flask, jsonify, request
from typing import Dict, Any, Optional

# Importing the InventoryManager from the core file
from main import InventoryManager

# --- ML Model Placeholder --- 

# Placeholder class for the ML model inference for future versions of it
# Must Import threading, time and random to function
"""class MLPredictor:
    #Simulates loading and running a trained TensorFlow model
    def __init__(self, model_path: str = "trained_model.h5"):
        # In a real environment, this would initialize the TensorFlow model
        self.model_path = model_path
        self.is_loaded = False
        self.device = self._get_optimal_device()
        self._loaded_model_sync() # Load a server start

    def _get_optimal_device(self) -> str:
        '''Checks for GPU availability for inference acceleration'''
        # SIMULATION:
        if random.random() < 0.5: # 50% chance to simulate a GPU being found
            return "GPU (RTX 3080)"
        return "CPU"
    
    def _load_model_sync(self):
        '''Simulates the blocking process of loading the trainel model file'''
        print(f"[{threading.current_thread().name}] Starting ML model loading...")
        #Simulates loading a large archive file (the trained model)
        time.sleep(random.uniform(0.5, 1.5))
        self.is_loaded = True
        print(f"[{threading.current_thread().name}] ML Model loaded successfully! Running on {self.device}")

    def predict_demand(self, item_id: int, hostorical_data: Dict[str, Any]) -> float:
        #Simulates running a prediction for future demand
        if not self.is_loaded:
            raise RuntimeError("Model is not loaded. Cannot run prediction")
        
        print(f"Running inference for item {item_id} on {self.device}...")

        #Simulate a prediction based on item_id (predictable but random)
        base_prediction = (item_id * 7 + random.randint(10, 50)) / 10
        #Simulate a complex, floating-point prediction
        return round(base_prediction * random.uniform(0.9, 1.1), 2)
    
        """
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
        quantity = int(data.get('quantity', 0))
        price = float(data.get('price', 0.0))

        if not name:
            return jsonify({"status": "error", "message": "Item name is required"}), 400
        
        # Call the core logic layer
        new_item = inventory_manager.add_item(name, quantity, price)

        return jsonify({
            "status": "success",
            "message": f"Item '{name}' added successfully.",
            "item": new_item.to_dict()
        }), 201 # HTTP 201 Created
    
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
    

# --- Run the APP ---
if __name__ == '__main__':
    print("\n--------------------------------------------")
    print("         Inventory API Server (SQLite) is starting...")
    print("       Acces the API endpoints using HTTP request at port 5000")
    print("----------------------------------------------")
    app.run(debug=True, host='0.0.0.0', port=5000)