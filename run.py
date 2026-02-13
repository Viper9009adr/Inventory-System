
from src.api import app

# --- Run the APP ---
if __name__ == '__main__':
    print("\n----------------------------------------------------------------")
    print("         Inventory API Server (SQLite) is starting...")
    print("       Acces the API endpoints using HTTP request at port 4999")
    print("------------------------------------------------------------------")
    app.run(debug=True, host='0.0.0.0', port=4999)