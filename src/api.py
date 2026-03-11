from flask import Flask, jsonify, request, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
from src.manager import InventoryManager
from src.database import Database_Initializer, DatabaseSession
from src.models import InventoryItem, ValidationError
from src.auth import limiter, require_auth, create_access_token, create_refresh_token, decode_token
from src.user_manager import register_users, login_user
import jwt
import click
import logging
from src.config import (
    REGISTER_RATE_LIMIT,
    LOGIN_RATE_LIMIT, 
    DB_NAME,
    WRITE_RATE_LIMIT,
    READ_RATE_LIMIT
    )

logger = logging.getLogger(__name__)

# --- Flask App Initialization ---
app = Flask(__name__)

# Attach rate limiter to app
limiter.init_app(app)

# Initialize the database once, no redundancy, even though is idempotent, it is more efficient this way. InventoryManager instance is created per HTTP request through each endpoint.
Database_Initializer.init_db(DB_NAME)

# Script to create first ADMIN role user
@app.cli.command("create-admin")
@click.argument("username")
@click.argument("password")
@with_appcontext
def create_admin(username, password):
    """
    Creates the first admin role.
    Use in terminal :  flask create-admin <username> <password>
    """
    hashed_password = generate_password_hash(password)
    try:
        with DatabaseSession(DB_NAME) as conn:
            conn.execute(
                "INSER INTO TABLE users (username, password, role) VALUES (?, ?, ?)",
                (username, hashed_password, "admin")
            )
        click.echo(f"User: {username} has been registered as admin")
    except Exception as e:
        click.echo(f"ERROR: {e}")



# --- API ENDPOINTS --- 
# ADMIN auth required, until roles implemented in full. Rate limit applied. 
@app.route('/api/register', methods=['POST'])
@limiter.limit(REGISTER_RATE_LIMIT)
@require_auth
def register():
    """
    Register a new user is protected for ADMIN users only, if <role> not specified , defaults to "member"
    
    Body: { " username ": "...", "email": "...", "password": "....", "role": "...."}
    Returns: access_token + refresh_token
    """
    data = request.get_json()
    if not data:
        return jsonify({"status":"error","message":"Missing JSON body"}, 400)
    # Tries to create the <user> on the DB, if success returns 
    try:
        user = register_users(
            username = str(data.get("username", "")),
            email = str(data.get("email", "")),
            password = str(data.get("password", "")),
            role = str(data.get("role", "member"))
        )
    except ValueError as e:
        return jsonify({"status":"error","message": str(e)}), 400
    
    access_token = create_access_token(user["user_id"], user["username"], user["role"] )
    refresh_token = create_refresh_token(user["user_id"], user["username"], user["role"])

    return jsonify({
        "status":"success",
        "message":"user registered succesfully",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type":"Bearer"
    }), 201

# rate limit applied
@app.route('/app/login', methods=['POST'])
@limiter.limit(LOGIN_RATE_LIMIT)
def login():
    """
    Login with username and password.
    
    Body : { "username" : "..." , "password" : "..." }
    Returns: access_token + refresh_token
    """

    data = request.get_json()
    if not data:
        return jsonify({
            "status":"error",
            "message":"Missing JSON body."}), 400
    
    user = login_user(
        username=data.get("username", ""),
        password=data.get("password", "")
    )
    # Will trigger same error whether username or password are wrong, this way prevents user enumeration.
    if not user:
        return jsonify({
            "status":"error",
            "message":"Invalidad credentials."
        }), 401
    
    access_token = create_access_token(user["user_id"], user["username"], user["role"])
    refresh_token = create_refresh_token(user["user_id"], user["username"], user["role"])

    return jsonify({
        "status":"success",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    }), 200

# refresh token endpoint
@app.route("/api/refresh", methods=['POST'])
@limiter.limit(LOGIN_RATE_LIMIT)
def refresh():
    """
    Exchange a refresh token for a new access token.
    
    Body: { "refresh_token": "..." }
    
    Access token expire in 1 hour by default, use the provided refresh_token that expires in 7 days, to generate a new access_token whitin that time-frame.
    This implementation aims to avoid re-login every hour
    """
    data = request.get_json()
    if not data or not data.get("refresh_token"):
        return jsonify({
            "status":"error",
            "message":"Missing refresh_token"
        }), 400
    
    try:
        payload = decode_token(data["refresh_token"])

        if payload.get("type") != "refresh":
            return jsonify({
                "status":"error",
                "message": "Invalid token type."
            }), 401
        
        # Role needs to be provided for create a new access token, there were two ways of implementing this:
        # 1 - Encoding the role and username in jwt.encode payload. This is superior in speed but can trigger mismatch if role get's changed on DB. Also relies on encoding algorithm.
        # 2 - Query the DB to retrieve the actual role, this adds latency and complexity to the code. 
        # For now, will use encode method.
        user_id = int(payload["sub"])
        username = str(payload["username"])
        role = str(payload["role"])


        new_access_token = create_access_token(user_id, username, role)

        return jsonify({
            "status": "success",
            "access_token": new_access_token,
            "token_type": "Bearer"
        }), 200
    
    except jwt.ExpiredSignatureError:
        return jsonify({
            "status":"error",
            "message": "Refresh token expired, Please login again."
        }), 401
    
    except jwt.InvalidTokenError:
        return jsonify({
            "status":"error",
            "message": "Invalid token"
        }), 401


# READ ALL ITEMS
# HTTP GET request to /api/inventory will list all items
@app.route('/api/inventory', methods=['GET'])
@limiter.limit(READ_RATE_LIMIT)
@require_auth
def get_inventory():
    #Endpoint to retrieve the entire inventory
    try:
        inventory_data = InventoryManager.get_all_items_data()
        return jsonify({
            "status": "success",
            "count": len(inventory_data),
            "inventory": inventory_data
        }), 200
    except Exception as e:
        print(f"Error fetching inventory: {e}")
        return jsonify({"status": "error", "message": "Failed to retrieve inventory data"}), 500
    

# CREATE ITEM
# HTTP POST request to /api/item with JSON body creates a new item
@app.route('/api/item', methods=['POST'])
@limiter.limit(WRITE_RATE_LIMIT)
@require_auth
def add_item_api():
    #Endpoint to add a new inventory item
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"status": "error", "message": "Missing JSON data in request."}), 400
        
        name = data.get("name")
        quantity = data.get('quantity')
        price = data.get('price')

        if not name:
            return jsonify({"status": "error", "message": "Item name is required"}), 400
        
        if quantity is None:
            return jsonify({"status": "error", "message": "Quantity is required"}), 400
        
        if price is None:
            return jsonify({"status": "error", "message": "Price is required"}), 400
        
        try:
            InventoryItem._validate_name(name)
            if not isinstance(quantity, int):
                raise ValidationError("Quantity must be an integer")
            InventoryItem._validate_quantity(quantity)

            if not isinstance(price, (int, float)):
                raise ValidationError("Price must be a number")
            InventoryItem._validate_price(price)

        except ValidationError as e:
            print(f"Error validation {e}")
            return jsonify({"status": "error", "message": str(e)}), 400
        
        new_item = InventoryManager.add_item(name, quantity, price)

        return jsonify({
            "status": "success",
            "message": f"Item '{name}' added successfully.",
            #"item": new_item.to_dict()
        }), 201 
    
    except Exception as e:
        print(f"Error adding item: {e}")
        return jsonify({"status": "error", "message": "Failed to add item."}), 500
    

# UPDATE ITEM
# HTTP PUT request to /api/item/<id> updates item details
@app.route('/api/item/<int:item_id>', methods=['PUT'])
@limiter.limit(WRITE_RATE_LIMIT)
@require_auth
def update_item_api(item_id):
    # Endpoint to update an existing Item by ID
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"status": "error", "message": "Missing JSON data in request."}), 400
    
        name = data.get('name')
        quantity = data.get('quantity')
        price = data.get('price')

        try:
            if quantity is not None:
                if not isinstance(quantity, int):
                    raise ValidationError("Quantity must be an integer")
                InventoryItem._validate_quantity(quantity)

            if price is not None:
                if not isinstance(price, (int, float)):
                    raise ValidationError("Price must be a number")
                InventoryItem._validate_price(price)
        except ValidationError as e:
            return jsonify({"status": "error", "message": str(e)}), 400

        was_updated = InventoryManager.update_item(
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
            }), 404 

    except Exception as e:
        print(f"Error updating item: {e}")
        return jsonify({"status": "error", "message": "Failed to update item."}), 500

# DELETE ITEM
# HTTP DELETE request to /api/item/<id> removes the item
@app.route('/api/item/<int:item_id>', methods=['DELETE'])
@limiter.limit(WRITE_RATE_LIMIT)
@require_auth
def delete_item_api(item_id):
    # Endpoint to delete an item by ID
    try:
        was_deleted = InventoryManager.delete_item(item_id)

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
        return jsonify({"status": "error", "message": "Failed to delete item."}), 500
    

# GET SINGLE ITEM
# HTTP GET request to /api/item/<id> retrieves single item
@app.route('/api/item/<int:item_id>', methods=['GET'])
@limiter.limit(READ_RATE_LIMIT)
@require_auth
def get_item_api(item_id):
    # Endpoint to retrieve a single item by ID
    try:
        data =  InventoryManager.get_item(item_id)

        if not data:
            return jsonify({"status": "error",
                            "message":"Item not found"}), 404
        
        return jsonify({
            "status": "success",
            "item": data
        }), 200


    except Exception as e:
        print(f"Error retrieving item: {e}")
        return jsonify({"status": "error", "message": "Failed to retrieve item."}), 500

