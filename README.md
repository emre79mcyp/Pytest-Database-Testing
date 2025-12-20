🏔️ Alps2Alps Backend QA Automation Framework
A production-ready Python automation framework designed to validate the core booking engine, pricing logic, and analytics pipeline for the Alps2Alps transfer service.

🏗️ Framework Architecture

This framework utilizes a layered design to separate concerns, ensuring that the test suite remains maintainable as the product scales.
•	Utility Layer (utils/): Stateless business logic (e.g., pricing math) that is unit-tested in isolation to ensure the "source of truth" is accurate.
•	Fixture Layer (conftest.py): Manages the database lifecycle, session-scoped connections, and per-test "clean slate" logic.
•	Test Layer (tests/): Domain-specific suites covering CRUD, API integration, and complex Data Pipelines.
•	Logging Layer: Integrated structured logging (test_run.log) for full auditability during CI/CD runs.
________________________________________

⚙️ Core Engineering Features

1. Database State & Isolation
The framework ensures Atomic Test Execution. The clean_database fixture resets all tables before every test, preventing data "leakage."
•	Foreign Key Enforcement: Uses PRAGMA foreign_keys = ON to ensure relational integrity.
•	Transaction Safety: Includes rollback() mechanisms in teardown fixtures to handle unexpected failures without corrupting the test environment.
2. Financial Precision & Consistency
To handle Alpine transfer discounts (like the 5% return leg discount), the framework avoids direct floating-point comparisons which are prone to binary rounding errors.
•	Strategy: Uses pytest.approx() with defined tolerances (rel=0.01) to validate price consistency between the Booking DB and the Analytics Event pipeline.
3. Modular Utility Layer
Instead of hardcoding math into assertions, the framework centralizes logic in utils/calculations.py.
•	Scalability: If business requirements change (e.g., the discount moves to 10%), we update one function instead of refactoring dozens of test files.
________________________________________
🔄 Data Pipeline Flow (Visualized)
The framework validates the synchronization between the operational database and the analytics reporting system.
1.	User Books: A simulated API call triggers a database insert.
2.	Persistence: Data is verified in the bookings table.
3.	Event Trigger: The system verifies an entry is created in booking_events.
4.	Consistency Check: A cross-table JOIN validates that booking.price == event.revenue.
________________________________________
📊 Test Coverage Summary
Category	Coverage Area	Status
API Integration	Validates API payloads correctly persist to DB	✅ Passing
Data Integrity	Foreign Key constraints & Orphaned record rejection	✅ Passing
Pricing Engine	Multi-route pricing & 5% Return-leg discounts	✅ Passing
Analytics Pipeline	Event-driven data flow & Revenue aggregation	✅ Passing
________________________________________
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
Senior QA Note: This framework is built for scalability. While currently using SQLite for portability, the abstraction in conftest.py allows for a seamless transition to a Dockerized PostgreSQL environment by simply updating the connection string.

