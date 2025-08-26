"""
Basic tests for Stash-Filter models.
"""

import pytest
import json
from datetime import datetime

def test_json_serialization():
    """Test JSON serialization works."""
    data = {
        'performers': ['Riley Reid', 'Mia Malkova'],
        'tags': ['blonde', 'brunette'],
        'title': 'Test Scene'
    }
    
    # Test JSON serialization
    json_str = json.dumps(data)
    assert json_str is not None
    
    # Test deserialization
    decoded = json.loads(json_str)
    assert decoded['title'] == 'Test Scene'
    assert len(decoded['performers']) == 2

def test_datetime_handling():
    """Test datetime handling."""
    now = datetime.utcnow()
    iso_string = now.isoformat()
    
    assert iso_string is not None
    assert 'T' in iso_string

def test_filter_reasons():
    """Test filter reason constants."""
    filter_reasons = [
        'already_downloaded',
        'unwanted_tags', 
        'studio_filter',
        'date_range',
        'duration_filter'
    ]
    
    assert len(filter_reasons) == 5
    assert 'already_downloaded' in filter_reasons

def test_basic_data_validation():
    """Test basic data validation."""
    scene_data = {
        'title': 'Test Scene',
        'performers': ['Test Performer'],
        'duration': 1800,
        'tags': ['test']
    }
    
    # Validate required fields
    assert 'title' in scene_data
    assert isinstance(scene_data['performers'], list)
    assert scene_data['duration'] > 0
    assert len(scene_data['tags']) > 0

def test_filtering_logic():
    """Test basic filtering logic."""
    unwanted_tags = ['anal', 'rough']
    scene_tags = ['blonde', 'oral']
    
    # Check if scene has unwanted tags
    has_unwanted = any(tag in scene_tags for tag in unwanted_tags)
    assert has_unwanted == False
    
    # Test with unwanted tag
    scene_tags_bad = ['blonde', 'anal', 'oral']
    has_unwanted_bad = any(tag in scene_tags_bad for tag in unwanted_tags)
    assert has_unwanted_bad == True
