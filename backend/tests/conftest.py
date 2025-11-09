"""
Test configuration and fixtures for ReasonOS backend
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def sample_data():
    """Sample test data"""
    return {
        "test_user": {
            "id": 1,
            "name": "Test User",
            "email": "test@example.com",
        }
    }
