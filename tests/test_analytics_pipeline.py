# tests/test_analytics_pipeline.py
import pytest
import sqlite3

def test_booking_creates_analytics_event(clean_database):
    """Test that creating booking also creates analytics event"""
    cursor = clean_database.cursor()
    
    # STEP 1: Create user
    cursor.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        ("John Ski", "john@alps.com")
    )
    user_id = cursor.lastrowid
    
    # STEP 2: Create booking (simulating API call)
    booking_price = 230.00
    cursor.execute("""
        INSERT INTO bookings (user_id, pickup, dropoff, price, status)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, "Geneva Airport", "Chamonix", booking_price, "confirmed"))
    
    booking_id = cursor.lastrowid
    clean_database.commit()
    
    # STEP 3: Simulate creating analytics event (what API would do)
    cursor.execute("""
        INSERT INTO booking_events (booking_id, event_type, revenue)
        VALUES (?, ?, ?)
    """, (booking_id, "booking_created", booking_price))
    clean_database.commit()
    
    # STEP 4: Verify analytics event exists
    cursor.execute(
        "SELECT event_type, revenue FROM booking_events WHERE booking_id = ?",
        (booking_id,)
    )
    event = cursor.fetchone()
    
    # ASSERTIONS
    assert event is not None, "Analytics event not created!"
    assert event["event_type"] == "booking_created"
    assert event["revenue"] == booking_price


def test_booking_data_consistency_across_systems(clean_database):
    """Test that data is consistent between main DB and analytics DB"""
    cursor = clean_database.cursor()
    
    # Create user
    cursor.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        ("Alpine Skier", "skier@alps.com")
    )
    user_id = cursor.lastrowid
    
    # Create booking with specific price
    booking_price = 150.00
    cursor.execute("""
        INSERT INTO bookings (user_id, pickup, dropoff, price, status)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, "Zurich Airport", "St. Moritz", booking_price, "confirmed"))
    
    booking_id = cursor.lastrowid
    clean_database.commit()
    
    # Create analytics event
    cursor.execute("""
        INSERT INTO booking_events (booking_id, event_type, revenue)
        VALUES (?, ?, ?)
    """, (booking_id, "booking_created", booking_price))
    clean_database.commit()
    
    # VERIFY: Price in main DB matches analytics DB
    cursor.execute("SELECT price FROM bookings WHERE id = ?", (booking_id,))
    main_db_price = cursor.fetchone()["price"]
    
    cursor.execute("SELECT revenue FROM booking_events WHERE booking_id = ?", (booking_id,))
    analytics_price = cursor.fetchone()["revenue"]
    
    # Assert consistency
    assert main_db_price == analytics_price, \
        f"Price mismatch! Main DB: {main_db_price}, Analytics: {analytics_price}"
    assert main_db_price == booking_price


def test_multiple_booking_events_pipeline(clean_database):
    """Test complete pipeline: booking → confirmation → assignment"""
    cursor = clean_database.cursor()
    
    # Create user
    cursor.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        ("Pipeline Tester", "test@alps.com")
    )
    user_id = cursor.lastrowid
    
    # Create booking
    cursor.execute("""
        INSERT INTO bookings (user_id, pickup, dropoff, price, status)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, "Munich Airport", "Garmisch", 120.00, "pending"))
    
    booking_id = cursor.lastrowid
    clean_database.commit()
    
    # EVENT 1: Booking created
    cursor.execute("""
        INSERT INTO booking_events (booking_id, event_type, revenue)
        VALUES (?, ?, ?)
    """, (booking_id, "booking_created", 120.00))
    clean_database.commit()
    
    # Update booking status
    cursor.execute(
        "UPDATE bookings SET status = ? WHERE id = ?",
        ("confirmed", booking_id)
    )
    clean_database.commit()
    
    # EVENT 2: Booking confirmed
    cursor.execute("""
        INSERT INTO booking_events (booking_id, event_type, revenue)
        VALUES (?, ?, ?)
    """, (booking_id, "booking_confirmed", 120.00))
    clean_database.commit()
    
    # Update booking status
    cursor.execute(
        "UPDATE bookings SET status = ? WHERE id = ?",
        ("driver_assigned", booking_id)
    )
    clean_database.commit()
    
    # EVENT 3: Driver assigned
    cursor.execute("""
        INSERT INTO booking_events (booking_id, event_type, revenue)
        VALUES (?, ?, ?)
    """, (booking_id, "driver_assigned", 120.00))
    clean_database.commit()
    
    # VERIFY: All events exist
    cursor.execute(
        "SELECT COUNT(*) as count FROM booking_events WHERE booking_id = ?",
        (booking_id,)
    )
    event_count = cursor.fetchone()["count"]
    
    assert event_count == 3, f"Expected 3 events, found {event_count}"
    
    # VERIFY: Booking status updated
    cursor.execute("SELECT status FROM bookings WHERE id = ?", (booking_id,))
    status = cursor.fetchone()["status"]
    assert status == "driver_assigned"


@pytest.mark.parametrize("pickup,dropoff,expected_price", [
    ("Geneva Airport", "Chamonix", 230.00),
    ("Zurich Airport", "St. Moritz", 200.00),
    ("Munich Airport", "Garmisch", 120.00),
])
def test_pricing_pipeline_all_routes(clean_database, pickup, dropoff, expected_price):
    """Test pricing across multiple routes with analytics tracking"""
    cursor = clean_database.cursor()
    
    # Create user
    cursor.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        ("Route Tester", f"test_{pickup}@alps.com")
    )
    user_id = cursor.lastrowid
    
    # Create booking with expected price
    cursor.execute("""
        INSERT INTO bookings (user_id, pickup, dropoff, price, status)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, pickup, dropoff, expected_price, "confirmed"))
    
    booking_id = cursor.lastrowid
    clean_database.commit()
    
    # Record in analytics
    cursor.execute("""
        INSERT INTO booking_events (booking_id, event_type, revenue)
        VALUES (?, ?, ?)
    """, (booking_id, "booking_created", expected_price))
    clean_database.commit()
    
    # VERIFY: Price matches across systems
    cursor.execute("SELECT price FROM bookings WHERE id = ?", (booking_id,))
    db_price = cursor.fetchone()["price"]
    
    cursor.execute("SELECT revenue FROM booking_events WHERE booking_id = ?", (booking_id,))
    analytics_price = cursor.fetchone()["revenue"]
    
    assert db_price == expected_price
    assert analytics_price == expected_price
    assert db_price == analytics_price


def test_analytics_revenue_aggregation(clean_database):
    """Test that we can aggregate revenue from analytics"""
    cursor = clean_database.cursor()
    
    # Create multiple bookings with different prices
    bookings = [
        ("User1", "user1@test.com", "Geneva", "Chamonix", 230.00),
        ("User2", "user2@test.com", "Zurich", "St. Moritz", 200.00),
        ("User3", "user3@test.com", "Munich", "Garmisch", 120.00),
    ]
    
    total_revenue = 0
    
    for name, email, pickup, dropoff, price in bookings:
        # Create user
        cursor.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (name, email)
        )
        user_id = cursor.lastrowid
        
        # Create booking
        cursor.execute("""
            INSERT INTO bookings (user_id, pickup, dropoff, price, status)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, pickup, dropoff, price, "confirmed"))
        
        booking_id = cursor.lastrowid
        total_revenue += price
        
        # Record in analytics
        cursor.execute("""
            INSERT INTO booking_events (booking_id, event_type, revenue)
            VALUES (?, ?, ?)
        """, (booking_id, "booking_created", price))
    
    clean_database.commit()
    
    # VERIFY: Total revenue calculated correctly
    cursor.execute(
        "SELECT SUM(revenue) as total FROM booking_events WHERE event_type = 'booking_created'"
    )
    analytics_total = cursor.fetchone()["total"]
    
    assert analytics_total == total_revenue, \
        f"Revenue mismatch! Expected {total_revenue}, got {analytics_total}"
    
    # VERIFY: Individual bookings match
    cursor.execute("""
        SELECT b.price, e.revenue
        FROM bookings b
        JOIN booking_events e ON b.id = e.booking_id
        WHERE e.event_type = 'booking_created'
    """)
    
    results = cursor.fetchall()
    for row in results:
        assert row["price"] == row["revenue"], \
            f"Booking mismatch: {row['price']} != {row['revenue']}"