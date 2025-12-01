# tests/test_database_crud.py
import pytest

def test_create_user(clean_database):
    """Test creating user in database"""
    cursor = clean_database.cursor()
    
    # Insert user
    cursor.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        ("Emre Ozgen", "emre@test.com")
    )
    clean_database.commit()
    
    # Verify user was created
    cursor.execute("SELECT * FROM users WHERE email = ?", ("emre@test.com",))
    user = cursor.fetchone()
    
    assert user is not None
    assert user["name"] == "Emre Ozgen"
    assert user["email"] == "emre@test.com"

def test_create_booking(clean_database):
    """Test creating booking in database"""
    cursor = clean_database.cursor()
    
    # First create a user
    cursor.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        ("Test User", "test@example.com")
    )
    user_id = cursor.lastrowid
    
    # Create booking
    cursor.execute("""
        INSERT INTO bookings (user_id, pickup, dropoff, price, status)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, "Geneva Airport", "Chamonix", 150.00, "confirmed"))
    
    clean_database.commit()
    
    # Verify booking
    cursor.execute("SELECT * FROM bookings WHERE user_id = ?", (user_id,))
    booking = cursor.fetchone()
    
    assert booking is not None
    assert booking["pickup"] == "Geneva Airport"
    assert booking["dropoff"] == "Chamonix"
    assert booking["price"] == 150.00
    assert booking["status"] == "confirmed"

def test_booking_user_relationship(clean_database):
    """Test relationship between bookings and users"""
    cursor = clean_database.cursor()
    
    # Create user
    cursor.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        ("John Smith", "john@example.com")
    )
    user_id = cursor.lastrowid
    
    # Create multiple bookings for same user
    bookings = [
        (user_id, "Geneva", "Chamonix", 150.00),
        (user_id, "Zurich", "St. Moritz", 200.00),
    ]
    
    cursor.executemany(
        "INSERT INTO bookings (user_id, pickup, dropoff, price) VALUES (?, ?, ?, ?)",
        bookings
    )
    clean_database.commit()
    
    # Query bookings for user
    cursor.execute("""
        SELECT u.name, b.pickup, b.dropoff, b.price
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        WHERE u.id = ?
    """, (user_id,))
    
    results = cursor.fetchall()
    
    assert len(results) == 2
    assert all(r["name"] == "John Smith" for r in results)

@pytest.mark.parametrize("pickup,dropoff,price", [
    ("Geneva Airport", "Chamonix", 120.00),
    ("Zurich Airport", "St. Moritz", 200.00),
    ("Milan Airport", "Cortina", 180.00),
])
def test_multiple_bookings(clean_database, pickup, dropoff, price):
    """Test creating bookings with different data"""
    cursor = clean_database.cursor()
    
    # Create user
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)",
                   ("Test User", f"test{price}@example.com"))
    user_id = cursor.lastrowid
    
    # Create booking
    cursor.execute(
        "INSERT INTO bookings (user_id, pickup, dropoff, price) VALUES (?, ?, ?, ?)",
        (user_id, pickup, dropoff, price)
    )
    clean_database.commit()
    
    # Verify
    cursor.execute("SELECT * FROM bookings WHERE user_id = ?", (user_id,))
    booking = cursor.fetchone()
    
    assert booking["pickup"] == pickup
    assert booking["dropoff"] == dropoff
    assert booking["price"] == price