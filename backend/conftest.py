"""
Pytest configuration and shared fixtures for the test suite.

This file is automatically discovered by pytest and contains:
- Global pytest configuration
- Shared fixtures used across all tests
"""

import pytest
import os
import sys

# Add parent directory to path so imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# =========================
# PYTEST CONFIGURATION
# =========================

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests (deselect with '-m \"not integration\"')"
    )
    config.addinivalue_line(
        "markers",
        "unit: marks tests as unit tests"
    )


# =========================
# PYTEST HOOKS
# =========================

@pytest.fixture(scope="session")
def setup_test_environment():
    """
    Setup test environment before running any tests.
    Runs once per test session.
    """
    # Set test mode
    os.environ['TESTING'] = 'true'
    
    print("\n" + "="*80)
    print("TEST SUITE INITIALIZATION")
    print("="*80)
    print("Running Billing & Sales Module Tests")
    print("Database: SQLite In-Memory")
    print("="*80 + "\n")
    
    yield
    
    print("\n" + "="*80)
    print("TEST SUITE COMPLETED")
    print("="*80 + "\n")
