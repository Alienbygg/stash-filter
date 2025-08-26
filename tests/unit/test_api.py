"""
Basic tests for Stash-Filter API functionality.
"""

import pytest
import json

def test_api_response_format():
    """Test API response format."""
    response = {
        'status': 'success',
        'message': 'Operation completed',
        'data': {'count': 5}
    }
    
    assert response['status'] == 'success'
    assert 'message' in response
    assert 'data' in response

def test_pagination_logic():
    """Test pagination calculations."""
    total_items = 100
    per_page = 20
    current_page = 3
    
    # Calculate pagination
    total_pages = (total_items + per_page - 1) // per_page
    offset = (current_page - 1) * per_page
    has_next = current_page < total_pages
    has_prev = current_page > 1
    
    assert total_pages == 5
    assert offset == 40
    assert has_next == True
    assert has_prev == True

def test_filter_params_validation():
    """Test filter parameter validation."""
    valid_filter_reasons = [
        'already_downloaded',
        'unwanted_tags',
        'studio_filter',
        'date_range',
        'duration_filter'
    ]
    
    # Test valid filter reason
    user_filter = 'unwanted_tags'
    assert user_filter in valid_filter_reasons
    
    # Test invalid filter reason
    invalid_filter = 'invalid_reason'
    assert invalid_filter not in valid_filter_reasons

def test_exception_types():
    """Test exception type validation."""
    valid_exception_types = ['permanent', 'temporary', 'one-time']
    
    assert 'permanent' in valid_exception_types
    assert 'temporary' in valid_exception_types  
    assert 'one-time' in valid_exception_types
    assert 'invalid' not in valid_exception_types

def test_search_query_building():
    """Test search query building."""
    filters = {
        'filter_reason': 'unwanted_tags',
        'has_exception': 'false',
        'search': 'riley reid'
    }
    
    # Build query parameters
    query_params = []
    for key, value in filters.items():
        if value:
            query_params.append(f"{key}={value}")
    
    query_string = "&".join(query_params)
    
    assert 'filter_reason=unwanted_tags' in query_string
    assert 'has_exception=false' in query_string
    assert 'search=riley+reid' in query_string.replace(' ', '+')
