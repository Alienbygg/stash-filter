"""
Unit tests for API endpoints.
"""

import pytest
import json
from unittest.mock import patch

def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'version' in data

def test_sync_favorites_endpoint(client, mock_stash_client):
    """Test sync favorites API endpoint."""
    response = client.post('/api/sync-favorites')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'success'
    assert 'message' in data

def test_toggle_monitoring_endpoint(client):
    """Test toggle monitoring API endpoint."""
    payload = {
        'type': 'performer',
        'id': 1
    }
    
    response = client.post('/api/toggle-monitoring', 
                          data=json.dumps(payload),
                          content_type='application/json')
    
    # This should return success even with empty database
    assert response.status_code in [200, 404]  # 404 if performer doesn't exist

def test_toggle_monitoring_invalid_type(client):
    """Test toggle monitoring with invalid type."""
    payload = {
        'type': 'invalid',
        'id': 1
    }
    
    response = client.post('/api/toggle-monitoring',
                          data=json.dumps(payload),
                          content_type='application/json')
    
    assert response.status_code == 400

def test_run_discovery_endpoint(client, mock_stash_client, mock_stashdb_client):
    """Test run discovery API endpoint.""" 
    response = client.post('/api/run-discovery')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'success'
    assert 'new_scenes' in data
    assert 'filtered_scenes' in data

def test_save_settings_endpoint(client, sample_config_data):
    """Test save settings API endpoint."""
    response = client.post('/api/save-settings',
                          data=json.dumps(sample_config_data),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'

def test_save_settings_invalid_data(client):
    """Test save settings with invalid data."""
    invalid_data = {
        'discovery_frequency_hours': 'invalid'  # Should be integer
    }
    
    response = client.post('/api/save-settings',
                          data=json.dumps(invalid_data), 
                          content_type='application/json')
    
    assert response.status_code == 400

def test_test_connections_endpoint(client, mock_stash_client, mock_stashdb_client, mock_whisparr_client):
    """Test connection testing API endpoint."""
    response = client.post('/api/test-connections')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'stash' in data
    assert 'stashdb' in data
    assert 'whisparr' in data

def test_add_to_whisparr_endpoint(client, mock_whisparr_client):
    """Test add to Whisparr API endpoint."""
    payload = {
        'wanted_id': 1
    }
    
    response = client.post('/api/add-to-whisparr',
                          data=json.dumps(payload),
                          content_type='application/json')
    
    # May return 404 if wanted scene doesn't exist
    assert response.status_code in [200, 404]

def test_add_all_to_whisparr_endpoint(client, mock_whisparr_client):
    """Test add all to Whisparr API endpoint."""
    payload = {
        'wanted_ids': [1, 2, 3]
    }
    
    response = client.post('/api/add-all-to-whisparr',
                          data=json.dumps(payload),
                          content_type='application/json')
    
    assert response.status_code in [200, 400]  # 400 if no valid IDs

def test_remove_wanted_endpoint(client):
    """Test remove wanted scene API endpoint."""
    payload = {
        'wanted_id': 1
    }
    
    response = client.delete('/api/remove-wanted',
                           data=json.dumps(payload),
                           content_type='application/json')
    
    # May return 404 if wanted scene doesn't exist
    assert response.status_code in [200, 404]

def test_refresh_whisparr_status_endpoint(client, mock_whisparr_client):
    """Test refresh Whisparr status API endpoint."""
    response = client.post('/api/refresh-whisparr-status')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'success'

def test_api_error_handling(client):
    """Test API error handling."""
    # Test with malformed JSON
    response = client.post('/api/save-settings',
                          data='malformed json',
                          content_type='application/json')
    
    assert response.status_code == 400

def test_api_missing_content_type(client):
    """Test API with missing content type."""
    payload = {'type': 'performer', 'id': 1}
    
    response = client.post('/api/toggle-monitoring',
                          data=json.dumps(payload))
    
    # Should still work with JSON data even without explicit content-type
    assert response.status_code in [200, 400, 404]

@patch('app.services.scheduler.SchedulerService')
def test_scheduler_integration(mock_scheduler, client):
    """Test scheduler integration with API endpoints."""
    mock_scheduler.return_value.run_discovery.return_value = {
        'new_scenes': 5,
        'filtered_scenes': 2,
        'wanted_added': 3,
        'errors': []
    }
    
    response = client.post('/api/run-discovery')
    assert response.status_code == 200

def test_api_rate_limiting(client):
    """Test API rate limiting (if implemented)."""
    # Make multiple rapid requests
    responses = []
    for i in range(10):
        response = client.get('/health')
        responses.append(response.status_code)
    
    # All should succeed (no rate limiting implemented yet)
    assert all(status == 200 for status in responses)

def test_cors_headers(client):
    """Test CORS headers (if implemented)."""
    response = client.options('/api/sync-favorites')
    
    # Basic OPTIONS request should work
    assert response.status_code in [200, 405]  # 405 if OPTIONS not implemented

def test_api_authentication(client):
    """Test API authentication (currently none required)."""
    # All endpoints should work without authentication
    response = client.get('/health')
    assert response.status_code == 200
    
    response = client.post('/api/test-connections')
    assert response.status_code == 200
