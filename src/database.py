"""
Database connection
"""
import sqlite3

class Database_Initializer:
    """
    Initializes the database using staticmethod.
    """

    @staticmethod
    def init_db(DB_NAME):
        """Creates the inventory table if it does not exist."""
        with DatabaseSession(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    item_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL, 
                    role TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
            ''')
            print(f"Sqlite database initialized: {DB_NAME}")
        

class DatabaseSession:
    """
    This class holds the context manager for the sqlite connection to the database, it ensures a safe rollback on exception raised.
    Uses idempotent configuration of Write Ahead Logging
    """
    def __init__(self, db_name):
        self.db_name = db_name

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL;")
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()