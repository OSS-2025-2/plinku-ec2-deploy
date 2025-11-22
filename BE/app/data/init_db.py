#PLINKU_PROJECT/BE/app/data/init_db.py
import sqlite3
from BE.app.config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Parking table (주차장 정보 테이블)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS parking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parking_name TEXT NOT NULL,
            address TEXT NOT NULL,
            price_per_hour INTEGER NOT NULL,
            total_spots INTEGER NOT NULL,
            available_spots INTEGER NOT NULL,
            distance_km REAL NOT NULL,
            ev_charger INTEGER DEFAULT 0,  -- 0 = False, 1 = True
            congestion TEXT,
            type TEXT
        );
    """)

    # ParkingSpot table (주차 공간 정보 테이블)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS parking_spot (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parking_id INTEGER NOT NULL,  -- 주차장 ID (외래 키)
            spot_id INTEGER NOT NULL,
            status TEXT NOT NULL,  -- "occupied", "available"
            color TEXT NOT NULL,   -- "red", "green" 등
            FOREIGN KEY (parking_id) REFERENCES parking (id)
        );
    """)

    # Buttons table (버튼 설정)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS parking_buttons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parking_id INTEGER NOT NULL,
            reserve_button INTEGER DEFAULT 0,  -- 0 = False, 1 = True
            route_button INTEGER DEFAULT 0,    -- 0 = False, 1 = True
            FOREIGN KEY (parking_id) REFERENCES parking (id)
        );
    """)

    # Reservation table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            parking_id INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (parking_id) REFERENCES parking(id)
        );
    """)

    conn.commit()
    conn.close()
