# tests/test_api_with_database.py
import sqlite3
import pytest

def test_simulated_api_creates_database_record(clean_database):
    cursor = clean_database.cursor()
    
    # STEP 1: Simulate API request creating user
    api_response_data = {
        "name": "API User",
        "email": "api@test.com"
    }
    
    # Simulate API creating user in database
    cursor.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        (api_response_data["name"], api_response_data["email"])
    )
    clean_database.commit()
    
    # Simulate API returning user_id
    user_id = cursor.lastrowid
    
    # STEP 2: Validate in database
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    db_user = cursor.fetchone()
    
    assert db_user is not None
    assert db_user["name"] == api_response_data["name"]
    assert db_user["email"] == api_response_data["email"]

def test_booking_price_calculation_validation(clean_database):
    cursor = clean_database.cursor()
    
    # Create user
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)",
                   ("Price Test", "price@test.com"))
    user_id = cursor.lastrowid
    
    # Pricing rules
    distance = 50
    base_rate = 50.00
    per_km_rate = 2.00
    expected_price = base_rate + (distance * per_km_rate)
    
    # Create booking with calculated price
    cursor.execute(
        "INSERT INTO bookings (user_id, pickup, dropoff, price) VALUES (?, ?, ?, ?)",
        (user_id, "Geneva", "Chamonix", expected_price)
    )
    
    clean_database.commit()
    
    # Validate price calculation
    cursor.execute("SELECT price FROM bookings WHERE user_id = ?", (user_id,))
    db_price = cursor.fetchone()["price"]
    
    assert db_price == expected_price
    assert db_price == 150.00

def test_data_integrity_foreign_key(clean_database):
    cursor = clean_database.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # This should fail because user_id 9999 doesn't exist
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            "INSERT INTO bookings (user_id, pickup, dropoff, price) VALUES (?, ?, ?, ?)",
            (9999, "Geneva", "Chamonix", 150.00)
        )
        clean_database.commit()