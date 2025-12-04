# tests/conftest.py
import pytest
import sqlite3
import os

@pytest.fixture
def db_connection():
    """Provide database connection for tests"""
    db_path = 'database/test_data.db'
    
    os.makedirs('database', exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    cursor = conn.cursor()
    
    # Existing tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            pickup TEXT NOT NULL,
            dropoff TEXT NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            status TEXT DEFAULT 'confirmed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # 🆕 NEW: Analytics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS booking_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            revenue DECIMAL(10,2),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booking_id) REFERENCES bookings(id)
        )
    """)
    
    cursor.execute("PRAGMA foreign_keys = ON")
    conn.commit()
    
    yield conn
    
    conn.close()

@pytest.fixture
def clean_database(db_connection):
    """Clean database before each test"""
    cursor = db_connection.cursor()
    # Delete in correct order (foreign keys!)
    cursor.execute("DELETE FROM booking_events")  # Delete dependent first
    cursor.execute("DELETE FROM bookings")
    cursor.execute("DELETE FROM users")
    db_connection.commit()
    yield db_connection