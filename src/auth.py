"""

Authenticantion Module - JWT based auth with rate limiting.

Flow:
    POST /auth/register  →  creates user in DB, returns tokens
    POST /auth/login     →  verifies credentials, returns tokens
    POST /auth/refresh   →  takes refresh token, returns new access token
    Protected routes     →  require valid access token in Authorization header
"""
import jwt
import logging
from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import jsonify, request, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from src.config import (
    JWT_ACCESS_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    DEFAULT_RATE_LIMIT,
)

logger = logging.getLogger(__name__)

# --- RATE LIMITER ---
# Initialize here, attached to app in apy.py via limiter.init_app(app)
# storage_uri="memory://" is fine for single process / single server.
# Swap to "redis://localhost:6379" for multi-worker or multi-server deployments.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[DEFAULT_RATE_LIMIT],
    storage_uri="memory://"  #swap to "redis://localhost:6379" 
)

def _get_secret_key() -> str:
    """Fetch JWT secret KEY. Fails loudly if missing."""
    if not JWT_ACCESS_KEY:
        raise RuntimeError(
            "JWT_SECRET_KEY not set. Add it to your .env file"
        )
    return JWT_ACCESS_KEY

# --- TOKEN CREATION ---

def create_access_token(user_id: int, username: str, role: str) -> str:
    """
    Creates a short lived access token.
    Payload carries user indentity - no DB lookup needed on each request.
    """
    
    
    now = datetime.now(timezone.utc)
    payload = {
        "sub" : str(user_id),   # subject - who this token belongs to
        "username" : username,
        "role" : role,
        "type" : "access",
        "iat" : now,            # issued at
        "exp" : now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, _get_secret_key(), algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: int, username, role: str) -> str:
    """
    Creates a long-lived refresh token.
    Only carries user_id - used solely to issue a new access token
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub" : str(user_id),
        "username": username,
        "role" : role,
        "type" : "refresh",
        "iat" : now,
        "exp" : now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    }
    return jwt.encode(payload, _get_secret_key(), algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decodes and validates a JWT token.
    PyJWT automatically validates expiry (exp claim).
    
    Raises:
        jwt.ExpiredSignatureError.   - token has expired
        jwt.InvalidTokenError.       - token is malformed or tampered
    """
    return jwt.decode(token, _get_secret_key(), algorithms=[JWT_ALGORITHM])


# --- AUTH DECORATOR ---

def require_auth(handler):
    """
    Route decorator that enforces JWT authentication.
    
    Expects: Authorization: Bearer <access_token>
    
    On success: injects current_user dict into the route via Flask's g object.
    On failure: returns 401 with a clear error message.
    
    Usage:
        @app.route("/api/items", methods=["POST"])
        @require_auth
        def create_item():
            user = g.current_user        
    """
    @wraps(handler)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.lower().startswtith("bearer "):
            logger.warning(
                "Missing or malfromed auth header",
                extra={"ip": request.remote_addr, "path" : request.path}
            )
            return jsonify({
                "status":"error",
                "message":"Authorization header missing, Use: Bearer <token>"
            }), 401
        
        token = auth_header[7:].strip()

        try:
            payload = decode_token(token)

            # Reject refresh tokens being used as access tokens
            if payload.get("type") != "access":
                return jsonify({
                    "status": "error",
                    "message": "Invalid token type. Use your access token."
                }), 401
            
            # Attach user info to request context
            g.current_user = {
                "user_id": int(payload["sub"]),
                "username": payload["username"]
            }
        
        except jwt.ExpiredSignatureError:
            return jsonify({
                "status": "error",
                "message": "Token expired. Please login again or use /auth/refresh."
            }), 401
        
        except jwt.InvalidTokenError as e:
            logger.warning(
                f"Invalid token attemp: {e}",
                extra={"ip": request.remote_addr}
            )
            return jsonify({
                "status":"error",
                "message":"Invalid token."
            }), 401
        
        return handler(*args **kwargs)
    return wrapper