"""
Simple working test configuration for Stash-Filter.
"""

import pytest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def mock_app_context():
    """Mock app context for testing."""
    return True

@pytest.fixture
def sample_data():
    """Sample data for testing."""
    return {
        'title': 'Test Scene',
        'performers': ['Test Performer'],
        'studio': 'Test Studio'
    }
