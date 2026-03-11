# Inventory System API

Flask-based inventory REST API with SQLite persistence, JWT authentication, rate limiting, and user management. Designed as a clean, minimal backend project and a baseline for future refactors to FastAPI/Django/PostgreSQL.

## Features

- Full CRUD API for inventory items
- SQLite persistence with safe parameterized queries and WAL mode
- JWT authentication (access + refresh tokens)
- User registration and login with hashed passwords (PBKDF2-SHA256)
- Per-route rate limiting via Flask-Limiter
- Validation rules for name, quantity, and price
- Pytest-based test suite

## Quick Start

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file from the template:
   ```bash
   cp env.example .env
   ```
   Generate a JWT secret key and set it in `.env`:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

4. Run the server:
   ```bash
   python run.py
   ```
   The server starts on `http://0.0.0.0:4999` by default.

5. Create the first admin user via the Flask CLI:
   ```bash
   flask create-admin <username> <password>
   ```

## Authentication

All inventory endpoints require a valid JWT access token. Tokens are obtained by logging in.

### Login

Request:
```bash
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}' \
  http://localhost:4999/app/login
```
Response:
```json
{
  "status": "success",
  "access_token": "<jwt-access-token>",
  "refresh_token": "<jwt-refresh-token>",
  "token_type": "Bearer"
}
```

### Using the Token

Pass the access token in the `Authorization` header:
```
Authorization: Bearer <access-token>
```

### Refresh Token

Access tokens expire after 1 hour (configurable). Use the refresh token (valid for 7 days) to get a new access token without re-logging in:

Request:
```bash
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<your-refresh-token>"}' \
  http://localhost:4999/api/refresh
```
Response:
```json
{
  "status": "success",
  "access_token": "<new-access-token>",
  "token_type": "Bearer"
}
```

### Register a New User (Admin Only)

Registration is protected and requires a valid admin access token:

Request:
```bash
curl -s -X POST \
  -H "Authorization: Bearer <admin-access-token>" \
  -H "Content-Type: application/json" \
  -d '{"username":"newuser","email":"user@example.com","password":"securepass","role":"member"}' \
  http://localhost:4999/api/register
```
Response:
```json
{
  "status": "success",
  "message": "user registered succesfully",
  "access_token": "<jwt-access-token>",
  "refresh_token": "<jwt-refresh-token>",
  "token_type": "Bearer"
}
```

## API Endpoints

| Method | Route | Auth | Rate Limit | Description |
|--------|-------|------|------------|-------------|
| POST | `/app/login` | No | 10/min | Login with username and password |
| POST | `/api/refresh` | No | 10/min | Exchange refresh token for new access token |
| POST | `/api/register` | JWT (admin) | 5/min | Register a new user |
| GET | `/api/inventory` | JWT | 60/min | List all inventory items |
| POST | `/api/item` | JWT | 30/min | Create a new item |
| GET | `/api/item/<id>` | JWT | 60/min | Get a single item by ID |
| PUT | `/api/item/<id>` | JWT | 30/min | Update an item by ID |
| DELETE | `/api/item/<id>` | JWT | 30/min | Delete an item by ID |

### List Inventory

Request:
```bash
curl -s \
  -H "Authorization: Bearer <access-token>" \
  http://localhost:4999/api/inventory
```
Response:
```json
{
  "status": "success",
  "count": 1,
  "inventory": [
    {
      "item_id": 1,
      "name": "Laptop",
      "quantity": 10,
      "price": 999.99
    }
  ]
}
```

### Create Item

Request:
```bash
curl -s -X POST \
  -H "Authorization: Bearer <access-token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Mouse","quantity":5,"price":19.99}' \
  http://localhost:4999/api/item
```
Response:
```json
{
  "status": "success",
  "message": "Item 'Mouse' added successfully."
}
```

### Get Item by ID

Request:
```bash
curl -s \
  -H "Authorization: Bearer <access-token>" \
  http://localhost:4999/api/item/1
```
Response:
```json
{
  "status": "success",
  "item": {
    "item_id": 1,
    "name": "Laptop",
    "quantity": 10,
    "price": 999.99
  }
}
```

### Update Item

Request:
```bash
curl -s -X PUT \
  -H "Authorization: Bearer <access-token>" \
  -H "Content-Type: application/json" \
  -d '{"quantity":12,"price":949.50}' \
  http://localhost:4999/api/item/1
```
Response:
```json
{
  "status": "success",
  "message": "Item ID 1 updated successfully."
}
```

### Delete Item

Request:
```bash
curl -s -X DELETE \
  -H "Authorization: Bearer <access-token>" \
  http://localhost:4999/api/item/1
```
Response:
```json
{
  "status": "success",
  "message": "Item ID 1 deteled successfully."
}
```

## Error Responses

- Validation errors return `400` with a message string.
- Missing/invalid/expired JWT token returns `401`.
- Rate limit exceeded returns `429`.
- Server-side failures return `500` with a generic message.

Example validation error:
```json
{
  "status": "error",
  "message": "Quantity must be an integer"
}
```

## Rate Limiting

All endpoints are rate-limited. Default limits (configurable via `.env`):

| Category | Default Limit |
|----------|---------------|
| Global default | 200 per hour |
| Login | 10 per minute |
| Registration | 5 per minute |
| Write operations (POST/PUT/DELETE) | 30 per minute |
| Read operations (GET) | 60 per minute |

Rate limiting uses in-memory storage by default. For multi-worker or multi-server deployments, switch to Redis by updating the storage URI in `src/auth.py`.

## Configuration

All configuration is loaded from environment variables (see `env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_NAME` | SQLite database filename | `inventory.db` |
| `JWT_ACCESS_KEY` | Secret key for signing JWTs | *(required)* |
| `JWT_ALGORITHM` | JWT signing algorithm | *(set in .env)* |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | `60` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | `7` |
| `DEFAULT_RATE_LIMIT` | Global rate limit | `200 per hour` |
| `LOGIN_RATE_LIMIT` | Login endpoint limit | `10 per minute` |
| `REGISTER_RATE_LIMIT` | Registration endpoint limit | `5 per minute` |
| `WRITE_RATE_LIMIT` | Write operations limit | `30 per minute` |
| `READ_RATE_LIMIT` | Read operations limit | `60 per minute` |
| `FLASK_DEBUG` | Enable debug mode | `false` |
| `HOST` | Server bind address | `0.0.0.0` |
| `PORT` | Server port | `4999` |

## Testing

Run all tests:
```bash
python -m pytest
```

Run a single test file:
```bash
python -m pytest tests/test_models.py
```

Run a single test by name:
```bash
python -m pytest tests/test_models.py -k test_inventory_item_name_too_long
```

Run with verbose output:
```bash
python -m pytest -v
```

## Project Structure

```
run.py                  # Server entry point
src/
  __init__.py           # Package init, version, exports
  api.py                # Flask routes and request handling
  auth.py               # JWT authentication, token creation/validation, rate limiter
  config.py             # Centralized configuration from environment variables
  database.py           # SQLite session context manager and DB initialization
  manager.py            # Inventory CRUD persistence logic
  models.py             # Data models, validation rules, custom exceptions
  user_manager.py       # User registration and login logic
tests/
  test_models.py        # Pytest suite for model and structure validation
env.example             # Template for .env configuration
```

## Validation Rules

- **name**: required, string, trimmed, max 255 characters
- **quantity**: required, integer, 0 to 1,000,000
- **price**: required, number, finite, 0.0 to 1,000,000.0

## Roadmap

- Refactor to a production-ready stack (FastAPI/Django + PostgreSQL)
- Add pagination, filtering, and sorting
- Add CI and linting/formatting
- Add role-based access control for all endpoints
- Add token revocation / blacklisting
