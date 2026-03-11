"""
Single source for all configuration

All values are pulled from environment variables with sensible defaults.
Set these in your .env file for local development.
In production, inject them via Docker or CI/CD pipeline.

"""

import os


# Database
DB_NAME = os.getenv("DB_NAME", "inventory.db")

# JWT
JWT_ACCESS_KEY = os.getenv("DB_NAME", "inventory.db")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
JWT_ALGORITHM = str(os.getenv("JWT_ALGORITHM"))

# RATE LIMIT
DEFAULT_RATE_LIMIT = os.getenv("DEFAULT_RATE_LIMIT", "200 per hour")
LOGIN_RATE_LIMIT = os.getenv("LOGIN_RATE_LIMIT", "10 per minute")
REGISTER_RATE_LIMIT = os.getenv("REGISTER_RATE_LIMIT", "5 per minute")
WRITE_RATE_LIMIT = os.getenv("WRITE_RATE_LIMIT", "30 per minute")
READ_RATE_LIMIT = os.getenv("READ_RATE_LIMIT", "60 per minute")

# APP
DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 4999))

