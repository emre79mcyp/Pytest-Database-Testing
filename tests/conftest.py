# tests/conftest.py
import pytest
import sqlite3
import os

@pytest.fixture
def db_connection():
    """Provide database connection for tests"""
    db_path = 'database/test_data.db'
    
    # Create database directory if doesn't exist
    os.makedirs('database', exist_ok=True)
    
    # Create connection
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Access columns by name
    
    # Create tables if they don't exist
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    
    # Create bookings table with foreign key - ADD STATUS COLUMN
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            pickup TEXT NOT NULL,
            dropoff TEXT NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            status TEXT DEFAULT 'confirmed',  -- ADD THIS COLUMN
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON")
    conn.commit()
    
    yield conn
    
    # Cleanup after test
    conn.close()

@pytest.fixture
def clean_database(db_connection):
    """Clean database before each test"""
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM bookings")
    cursor.execute("DELETE FROM users")
    db_connection.commit()
    yield db_connection