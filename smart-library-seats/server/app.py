import sqlite3
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import os
import logging

app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@app.route('/tools/<path:filename>')
def serve_tools(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'tools'), filename)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seatify.db")

def init_db():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            # Floor stats for dashboard analytics
            conn.execute("""
                CREATE TABLE IF NOT EXISTS floor_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    floor_id INTEGER,
                    available INTEGER,
                    occupied INTEGER,
                    reserved INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Staff Authentication
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    role TEXT DEFAULT 'staff'
                )
            """)
            # Reservation Tracking
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reservations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    seat_id TEXT,
                    floor_id INTEGER,
                    user_id INTEGER,
                    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    end_time DATETIME
                )
            """)
            # Granular Seat History (for Heatmaps)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS seat_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    seat_id TEXT,
                    floor_id INTEGER,
                    status TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Seed default admin if not exists
            conn.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
            
            conn.commit()
            logging.info("SQLite initialized with extended tables.")
    except Exception as e:
        logging.error(f"SQLite init error: {e}")

init_db()

# Initialize 8 floors with default empty data
floor_data = {
    str(i): {
        "available": 0, "occupied": 0, "reserved": 0, 
        "seats": {}, "last_updated": "Initializing..."
    } for i in range(1, 9)
}
inference_config = {"mode": "video", "source": "tools/library_video.mp4", "floor_id": 1}

@app.route("/config", methods=["GET", "POST"])
def manage_config():
    if request.method == "POST":
        data = request.json
        for key in ["mode", "source", "floor_id"]:
            if key in data:
                inference_config[key] = data[key]
        return jsonify({"message": "Config updated", "config": inference_config}), 200
    return jsonify(inference_config)

@app.route("/update", methods=["POST"])
def update_status():
    data = request.json
    floor_id = int(data.get("floor_id", 1))

    floor_data[str(floor_id)] = {
        "available": data.get("available", 0),
        "occupied": data.get("occupied", 0),
        "reserved": data.get("reserved", 0),
        "seats": data.get("seats", {}),
        "boxes": data.get("boxes", []),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    logging.info(f"Updated floor {floor_id}. Global keys: {list(floor_data.keys())}")

    # Log to DB (Floor aggregate)
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO floor_stats (floor_id, available, occupied, reserved) VALUES (?, ?, ?, ?)",
                (floor_id, data.get("available", 0), data.get("occupied", 0), data.get("reserved", 0))
            )
            
            # Log seat-level changes if provided
            seats = data.get("seats", {})
            for sid, status in seats.items():
                conn.execute(
                    "INSERT INTO seat_logs (seat_id, floor_id, status) VALUES (?, ?, ?)",
                    (sid, floor_id, status)
                )
            conn.commit()
    except Exception as e:
        logging.error(f"DB update error: {e}")

    return jsonify({"message": "Updated"}), 200


@app.route("/status/<floor_id>")
def get_status(floor_id):
    return jsonify(floor_data.get(str(floor_id), {
        "available": 0, "occupied": 0, "reserved": 0, 
        "seats": {}, "last_updated": "Never"
    }))

@app.route("/floors")
def get_floors():
    logging.info(f"Serving /floors. Data keys: {list(floor_data.keys())}")
    return jsonify(floor_data)

@app.route("/analytics")
def get_analytics():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT strftime('%H', timestamp) as hour, AVG(occupied) as avg_occ
                FROM floor_stats
                GROUP BY hour
                ORDER BY avg_occ DESC
            """)
            rows = cursor.fetchall()
            
            peak_hour = rows[0]["hour"] if rows else "NA"
            free_hour = rows[-1]["hour"] if rows else "NA"
            
            return jsonify({
                "peak_hour": f"{peak_hour}:00",
                "free_hour": f"{free_hour}:00",
                "history": [dict(r) for r in rows]
            })
    except:
        return jsonify({"peak_hour": "NA:00", "free_hour": "NA:00", "history": []})

@app.route("/seat-map")
def get_seat_map():
    SEAT_MAP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cam1", "seats_cam1.json")
    if os.path.exists(SEAT_MAP_PATH):
        try:
            with open(SEAT_MAP_PATH, "r") as f:
                return jsonify(json.load(f))
        except: pass
    return jsonify([])

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
            if user:
                return jsonify({"status": "success", "user": dict(user)})
            return jsonify({"status": "fail", "message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/reserve", methods=["POST"])
def reserve():
    data = request.json
    seat_id = data.get("seat_id")
    floor_id = data.get("floor_id")
    user_id = data.get("user_id", 1) # Default to admin if not specified
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("INSERT INTO reservations (seat_id, floor_id, user_id) VALUES (?, ?, ?)", 
                         (seat_id, floor_id, user_id))
            conn.commit()
            return jsonify({"status": "success", "message": f"Seat {seat_id} reserved"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/activity-logs")
def get_activity_logs():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            # Get last 100 seat status changes
            logs = conn.execute("SELECT * FROM seat_logs ORDER BY timestamp DESC LIMIT 100").fetchall()
            return jsonify([dict(l) for l in logs])
    except Exception as e:
        return jsonify([])


if __name__ == "__main__":
    app.run(port=8000, debug=False)
