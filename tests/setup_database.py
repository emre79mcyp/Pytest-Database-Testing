# setup_database.py
import sqlite3

def setup_test_database():
    """Create a test database file for development"""
    conn = sqlite3.connect('test_database.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    
    # Create bookings table with foreign key
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            pickup TEXT NOT NULL,
            dropoff TEXT NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON")
    
    conn.commit()
    conn.close()
    print("Test database created successfully!")

if __name__ == "__main__":
    setup_test_database()