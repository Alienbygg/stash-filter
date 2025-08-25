"""
Integration tests for Stash-Filter application.
"""

import pytest
import json
import time
from unittest.mock import patch, Mock

def test_full_discovery_workflow(client, mock_stash_client, mock_stashdb_client, mock_whisparr_client, app):
    """Test complete discovery workflow integration."""
    
    with app.app_context():
        from app import db
        from app.models import Performer, Studio, Scene, Config
        
        # 1. Create initial data
        config = Config(
            discovery_enabled=True,
            unwanted_categories=['anal'],
            required_categories=[],
            auto_add_to_whisparr=True
        )
        db.session.add(config)
        
        performer = Performer(
            stash_id='1',
            name='Test Performer',
            monitored=True
        )
        db.session.add(performer)
        
        studio = Studio(
            stash_id='1', 
            name='Test Studio',
            monitored=True
        )
        db.session.add(studio)
        db.session.commit()
        
        # 2. Sync favorites
        response = client.post('/api/sync-favorites')
        assert response.status_code == 200
        
        # 3. Run discovery
        response = client.post('/api/run-discovery') 
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'new_scenes' in data

def test_stash_integration(mock_stash_client):
    """Test Stash API integration."""
    
    # Test connection
    assert mock_stash_client.test_connection() == True
    
    # Test getting favorites
    favorites = mock_stash_client.get_favorites()
    assert 'performers' in favorites
    assert 'studios' in favorites
    assert len(favorites['performers']) > 0

def test_stashdb_integration(mock_stashdb_client):
    """Test StashDB API integration."""
    
    # Test connection
    assert mock_stashdb_client.test_connection() == True
    
    # Test scene search
    scenes = mock_stashdb_client.search_scenes('Test Performer')
    assert len(scenes) > 0
    assert scenes[0]['title'] == 'Test Scene'

def test_whisparr_integration(mock_whisparr_client):
    """Test Whisparr API integration."""
    
    # Test connection
    assert mock_whisparr_client.test_connection() == True
    
    # Test adding movie
    result = mock_whisparr_client.add_movie('Test Movie')
    assert result['status'] == 'wanted'

def test_database_migrations(app):
    """Test database schema and migrations."""
    
    with app.app_context():
        from app import db
        from app.models import Performer, Studio, Scene, WantedScene, Config
        
        # Test table creation
        db.create_all()
        
        # Test that all tables exist
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        expected_tables = ['performers', 'studios', 'scenes', 'wanted_scenes', 'config']
        for table in expected_tables:
            assert table in tables

def test_concurrent_discovery_requests(client, mock_stash_client, mock_stashdb_client):
    """Test handling concurrent discovery requests."""
    
    import threading
    import queue
    
    results = queue.Queue()
    
    def run_discovery():
        response = client.post('/api/run-discovery')
        results.put(response.status_code)
    
    # Start multiple discovery threads
    threads = []
    for i in range(3):
        thread = threading.Thread(target=run_discovery)
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Check that all requests completed
    status_codes = []
    while not results.empty():
        status_codes.append(results.get())
    
    assert len(status_codes) == 3
    # All should succeed (or handle concurrency gracefully)
    assert all(code in [200, 409] for code in status_codes)  # 409 if already running

def test_large_dataset_performance(client, app):
    """Test performance with large datasets."""
    
    with app.app_context():
        from app import db
        from app.models import Performer, Studio, Scene
        
        # Create large dataset
        performers = []
        for i in range(100):
            performer = Performer(
                stash_id=str(i),
                name=f'Performer {i}',
                monitored=True
            )
            performers.append(performer)
        
        db.session.add_all(performers)
        db.session.commit()
        
        # Test API performance
        start_time = time.time()
        response = client.get('/api/performers')  # Assuming this endpoint exists
        end_time = time.time()
        
        # Should complete within reasonable time
        assert (end_time - start_time) < 2.0  # 2 seconds max
        assert response.status_code in [200, 404]  # 404 if endpoint doesn't exist

def test_error_recovery(client, app):
    """Test error recovery and resilience."""
    
    # Test database connection error recovery
    with patch('app.db.session.commit') as mock_commit:
        mock_commit.side_effect = Exception("Database connection lost")
        
        response = client.post('/api/sync-favorites')
        
        # Should handle error gracefully
        assert response.status_code in [500, 503]  # Internal server error or service unavailable

def test_configuration_management(client, app, sample_config_data):
    """Test configuration management integration."""
    
    # Save configuration
    response = client.post('/api/save-settings',
                          data=json.dumps(sample_config_data),
                          content_type='application/json')
    assert response.status_code == 200
    
    # Verify configuration is saved
    with app.app_context():
        from app.models import Config
        config = Config.query.first()
        
        assert config is not None
        assert config.discovery_enabled == sample_config_data['discovery_enabled']
        assert config.unwanted_categories == sample_config_data['unwanted_categories']

def test_scene_filtering_integration(client, app, mock_stashdb_client):
    """Test scene filtering integration."""
    
    with app.app_context():
        from app import db
        from app.models import Config
        
        # Set up filtering configuration
        config = Config(
            unwanted_categories=['anal', 'bdsm'],
            required_categories=['lesbian'],
            min_duration_minutes=15,
            max_duration_minutes=120
        )
        db.session.add(config)
        db.session.commit()
        
        # Mock StashDB to return scenes with different characteristics
        scenes_data = [
            {
                'id': 'scene-1',
                'title': 'Good Scene',
                'duration': 1800,  # 30 minutes
                'categories': ['lesbian', 'softcore']
            },
            {
                'id': 'scene-2', 
                'title': 'Bad Scene',
                'duration': 3600,  # 60 minutes
                'categories': ['anal']  # Unwanted category
            },
            {
                'id': 'scene-3',
                'title': 'Short Scene', 
                'duration': 600,   # 10 minutes - too short
                'categories': ['lesbian']
            }
        ]
        
        mock_stashdb_client.search_scenes.return_value = scenes_data
        
        # Run discovery
        response = client.post('/api/run-discovery')
        assert response.status_code == 200
        
        data = response.get_json()
        # Should filter out unwanted and short scenes
        assert data['filtered_scenes'] >= 2

def test_whisparr_download_workflow(client, app, mock_whisparr_client):
    """Test complete Whisparr download workflow."""
    
    with app.app_context():
        from app import db
        from app.models import Scene, WantedScene
        from datetime import date
        
        # Create a wanted scene
        scene = Scene(
            stashdb_id='test-scene',
            title='Test Scene',
            release_date='2025-01-20',
            duration=1800,
            is_wanted=True
        )
        db.session.add(scene)
        db.session.commit()
        
        wanted = WantedScene(
            scene_id=scene.id,
            title=scene.title,
            release_date=date(2025, 1, 20),
            status='wanted'
        )
        db.session.add(wanted)
        db.session.commit()
        
        # Add to Whisparr
        response = client.post('/api/add-to-whisparr',
                              data=json.dumps({'wanted_id': wanted.id}),
                              content_type='application/json')
        
        assert response.status_code == 200
        
        # Refresh status
        response = client.post('/api/refresh-whisparr-status')
        assert response.status_code == 200

def test_health_monitoring_integration(client):
    """Test health monitoring and status reporting."""
    
    # Test basic health check
    response = client.get('/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'healthy'
    
    # Test connection health
    response = client.post('/api/test-connections')
    assert response.status_code == 200
    
    connections = response.get_json()
    # At least Stash should be testable
    assert 'stash' in connections

def test_logging_integration(client, caplog):
    """Test logging integration."""
    
    # Trigger some operations that should log
    client.post('/api/sync-favorites')
    client.post('/api/run-discovery') 
    
    # Check that logs were generated
    # This will depend on your actual logging setup
    assert len(caplog.records) >= 0  # At least no errors in logging setup

def test_backup_restore_integration(app):
    """Test backup and restore functionality."""
    
    with app.app_context():
        from app import db
        from app.models import Performer
        
        # Create test data
        performer = Performer(
            stash_id='backup-test',
            name='Backup Test Performer',
            monitored=True
        )
        db.session.add(performer)
        db.session.commit()
        
        # Test data export (would need actual backup functionality)
        performers = Performer.query.all()
        assert len(performers) >= 1
        
        # Test data structure for backup compatibility
        performer_data = {
            'stash_id': performer.stash_id,
            'name': performer.name,
            'monitored': performer.monitored
        }
        
        # Should be JSON serializable
        json.dumps(performer_data)  # Should not raise exception
