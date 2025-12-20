Framework Architecture
This framework utilizes a layered design to separate concerns, making it highly maintainable and scalable:
•	Utility Layer (utils/): Statistically independent business logic (e.g., pricing math) that can be unit-tested in isolation.
•	Fixture Layer (conftest.py): Manages the database lifecycle, session-scoped connections, and per-test "clean slate" logic.
•	Test Layer (tests/): Domain-specific suites covering CRUD, API integration, and complex Data Pipelines.
•	Logging Layer: Integrated structured logging for debugging test runs in CI/CD environments.
📂 Project Structure
Plaintext
project/
├── database/
│   └── test_data.db          # Auto-created SQLite database
├── utils/
│   ├── __init__.py
│   └── calculations.py       # Modular business logic (Pricing, Rounding)
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Database fixtures & Advanced Logging
│   ├── test_analytics.py     # Pipeline & Data Consistency tests
│   ├── test_api_db.py        # API + DB Integration
│   └── test_database_crud.py # Table-level validation
├── pytest.ini                # Test runner configuration (pythonpath, html reports)
├── test_run.log              # Auto-generated execution logs
└── README.md
⚙️ Core Engineering Features
1. Database State & Isolation
The framework ensures Atomic Test Execution. The clean_database fixture resets all tables before every test, preventing data "leakage" or pollution.
•	Foreign Key Enforcement: Uses PRAGMA foreign_keys = ON to ensure relational integrity.
•	Transaction Safety: Includes rollback() mechanisms in teardown fixtures to handle unexpected failures.
2. Financial Precision & Consistency
To handle Alpine transfer discounts (like the 5% return leg discount), the framework avoids direct floating-point comparisons.
•	Strategy: Uses pytest.approx() with defined tolerances (rel=0.01) to validate price consistency between the Booking DB and the Analytics Event pipeline.
3. Modular Utility Layer
Instead of hardcoding math into assertions, the framework uses a dedicated utils/calculations.py.
•	Benefit: If Alps2Alps changes their discount policy, we update one utility function instead of refactoring dozens of test files.
🧪 Running the Suite
Prerequisites
Bash
pip install pytest pytest-html pytest-metadata
Execution Commands
Bash
# Run all tests with verbose output and HTML report
pytest

# Run specific domain suites
pytest tests/test_analytics_pipeline.py -v

# Check execution logs for debugging
cat test_run.log
📊 Test Coverage Summary
Category	Coverage Area	Status
API Integration	Validates API payloads correctly persist to DB	✅ Passing
Data Integrity	Foreign Key constraints & Orphaned record rejection	✅ Passing
Pricing Engine	Multi-route pricing & 5% Return-leg discounts	✅ Passing
Analytics Pipeline	Event-driven data flow & Revenue aggregation	✅ Passing
🎯 Key Test Highlights
•	test_booking_data_consistency_across_systems: High-priority test ensuring that the revenue reported in Analytics exactly matches the price charged in the Booking system.
•	test_booking_fails_without_valid_user: A negative test validating that the database layer protects against corrupted or orphaned data.
•	test_analytics_revenue_aggregation: Validates SUM() and JOIN queries to ensure financial reporting accuracy.
________________________________________
Senior QA Note: This framework is built for scalability. While currently using SQLite, the abstraction in conftest.py allows for a seamless transition to a Dockerized PostgreSQL environment by simply updating the connection string.
