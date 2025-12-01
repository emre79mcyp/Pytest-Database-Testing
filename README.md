This project uses SQLite + pytest fixtures to simulate API/database operations in a clean and isolated environment.
Each test runs against a temporary SQLite test database created inside the database/ folder.

📌 Project Structure
project/
│
├── database/
│   └── test_data.db           # auto-created when tests run
│
├── tests/
│   ├── conftest.py            # pytest fixtures (DB setup, cleanup)
│   ├── test_api_with_database.py
│   └── test_database_crud.py
│
└── setup_database.py          # helper script to manually create a DB

⚙️ Fixtures Overview (conftest.py)
### 🔹 db_connection Fixture

Creates database/test_data.db if it doesn’t exist

Enables foreign keys

Creates required tables:

users(id, name, email)
bookings(
    id,
    user_id,
    pickup,
    dropoff,
    price,
    status DEFAULT 'confirmed'
)


Provides a live SQLite connection to tests

Closes the DB after tests complete

🔹 clean_database Fixture

Executed before every test:

Deletes all rows from users

Deletes all rows from bookings

Ensures every test starts with a fresh database

🧪 Running Tests

Make sure dependencies are installed:

pip install pytest


Run all tests:

pytest -v


Run a single file:

pytest tests/test_api_with_database.py -v

📘 What the Tests Cover
✔ Create user using simulated API

test_simulated_api_creates_database_record
Ensures inserting a user through simulated API logic matches what is stored in the DB.

✔ Price calculation validation

test_booking_price_calculation_validation
Checks that business logic for pricing is stored correctly.

✔ Foreign key integrity

test_data_integrity_foreign_key
Asserts SQLite raises IntegrityError when referencing a non-existent user.

✔ CRUD operations

test_create_user, test_create_booking
Validates CREATE functionality for both tables.

✔ User–Booking relationship

test_booking_user_relationship
Ensures JOIN queries return correct relational data.

✔ Parameterized booking tests

test_multiple_bookings
Creates multiple bookings with different parameters.
