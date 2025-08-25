"""
Test configuration and fixtures for Stash-Filter tests.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from app import create_app, db

@pytest.fixture
def app():
    """Create application for testing."""
    
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp()
    
    # Configure test app
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False
    }
    
    # Create app with test config
    app = create_app('testing')
    app.config.update(test_config)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test runner."""
    return app.test_cli_runner()

@pytest.fixture
def mock_stash_client():
    """Mock Stash client for testing."""
    with patch('app.services.stash_client.StashClient') as mock:
        client = Mock()
        client.test_connection.return_value = True
        client.get_favorites.return_value = {
            'performers': [
                {'id': '1', 'name': 'Test Performer', 'stashdb_id': 'test-123'}
            ],
            'studios': [
                {'id': '1', 'name': 'Test Studio', 'stashdb_id': 'studio-123'}
            ]
        }
        client.scene_exists.return_value = False
        mock.return_value = client
        yield client

@pytest.fixture
def mock_stashdb_client():
    """Mock StashDB client for testing."""
    with patch('app.services.stashdb_client.StashDBClient') as mock:
        client = Mock()
        client.test_connection.return_value = True
        client.search_scenes.return_value = [
            {
                'id': 'scene-123',
                'title': 'Test Scene',
                'release_date': '2025-01-20',
                'duration': 1800,
                'performers': ['Test Performer'],
                'studio': 'Test Studio',
                'tags': ['test', 'scene']
            }
        ]
        mock.return_value = client
        yield client

@pytest.fixture
def mock_whisparr_client():
    """Mock Whisparr client for testing."""
    with patch('app.services.whisparr_client.WhisparrClient') as mock:
        client = Mock()
        client.test_connection.return_value = True
        client.add_movie.return_value = {'id': 123, 'status': 'wanted'}
        client.get_movie_status.return_value = 'downloading'
        mock.return_value = client
        yield client

@pytest.fixture
def sample_scene_data():
    """Sample scene data for testing."""
    return {
        'stashdb_id': 'test-scene-123',
        'title': 'Test Scene Title',
        'release_date': '2025-01-20',
        'duration': 1800,
        'tags': ['lesbian', 'blonde'],
        'categories': ['softcore'],
        'performer_id': 1,
        'studio_id': 1
    }

@pytest.fixture
def sample_performer_data():
    """Sample performer data for testing."""
    return {
        'stash_id': '1',
        'stashdb_id': 'performer-abc-123',
        'name': 'Test Performer',
        'aliases': ['Test Alias'],
        'monitored': True
    }

@pytest.fixture
def sample_studio_data():
    """Sample studio data for testing."""
    return {
        'stash_id': '1', 
        'stashdb_id': 'studio-xyz-456',
        'name': 'Test Studio',
        'parent_studio': 'Parent Studio',
        'monitored': True
    }

@pytest.fixture
def sample_config_data():
    """Sample configuration data for testing."""
    return {
        'unwanted_categories': ['anal', 'bdsm'],
        'required_categories': ['lesbian'],
        'discovery_enabled': True,
        'discovery_frequency_hours': 24,
        'max_scenes_per_check': 100,
        'min_duration_minutes': 10,
        'max_duration_minutes': 180,
        'auto_add_to_whisparr': True,
        'whisparr_quality_profile': 'HD'
    }

# Test environment variables
@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        'STASH_URL': 'http://test-stash:9999',
        'STASH_API_KEY': 'test-stash-api-key',
        'WHISPARR_URL': 'http://test-whisparr:6969',
        'WHISPARR_API_KEY': 'test-whisparr-api-key',
        'STASHDB_API_KEY': 'test-stashdb-api-key',
        'SECRET_KEY': 'test-secret-key',
        'DATABASE_PATH': ':memory:',
        'LOG_LEVEL': 'DEBUG'
    }
    
    with patch.dict(os.environ, env_vars):
        yield

class MockResponse:
    """Mock HTTP response for testing."""
    
    def __init__(self, json_data=None, status_code=200, text=""):
        self.json_data = json_data or {}
        self.status_code = status_code
        self.text = text
        
    def json(self):
        return self.json_data
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

@pytest.fixture
def mock_requests():
    """Mock requests library for testing."""
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post:
        
        # Default successful responses
        mock_get.return_value = MockResponse({'status': 'ok'})
        mock_post.return_value = MockResponse({'status': 'success'})
        
        yield {'get': mock_get, 'post': mock_post}
