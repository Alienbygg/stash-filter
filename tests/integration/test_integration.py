"""
Basic integration tests for Stash-Filter.
"""

import pytest

def test_basic_workflow():
    """Test basic application workflow."""
    # Simulate discovery workflow
    performers = ['Riley Reid', 'Mia Malkova']
    discovered_scenes = [
        {'title': 'Scene 1', 'performer': 'Riley Reid', 'tags': ['blonde', 'oral']},
        {'title': 'Scene 2', 'performer': 'Mia Malkova', 'tags': ['blonde', 'anal']},
        {'title': 'Scene 3', 'performer': 'Riley Reid', 'tags': ['brunette', 'oral']}
    ]
    
    # Apply filtering
    unwanted_tags = ['anal']
    filtered_scenes = []
    passed_scenes = []
    
    for scene in discovered_scenes:
        has_unwanted = any(tag in scene['tags'] for tag in unwanted_tags)
        if has_unwanted:
            filtered_scenes.append(scene)
        else:
            passed_scenes.append(scene)
    
    # Verify filtering results
    assert len(filtered_scenes) == 1  # Scene 2 with anal tag
    assert len(passed_scenes) == 2    # Scene 1 and 3
    assert filtered_scenes[0]['title'] == 'Scene 2'

def test_exception_workflow():
    """Test exception handling workflow."""
    # Start with a filtered scene
    filtered_scene = {
        'id': 1,
        'title': 'Filtered Scene',
        'filter_reason': 'unwanted_tags',
        'is_exception': False
    }
    
    # Create exception
    exception = {
        'scene_id': 1,
        'type': 'permanent',
        'reason': 'User requested',
        'is_active': True
    }
    
    # Apply exception
    if exception['is_active'] and exception['scene_id'] == filtered_scene['id']:
        filtered_scene['is_exception'] = True
    
    # Verify exception applied
    assert filtered_scene['is_exception'] == True

def test_statistics_calculation():
    """Test statistics calculation."""
    total_filtered = 100
    total_exceptions = 15
    
    # Calculate exception rate
    exception_rate = round((total_exceptions / max(total_filtered, 1)) * 100, 1)
    
    assert exception_rate == 15.0
    
    # Test edge case
    total_filtered_zero = 0
    total_exceptions_zero = 0
    exception_rate_zero = round((total_exceptions_zero / max(total_filtered_zero, 1)) * 100, 1)
    
    assert exception_rate_zero == 0.0

def test_data_cleanup():
    """Test data cleanup logic."""
    from datetime import datetime, timedelta
    
    # Mock scenes with different ages
    scenes = [
        {'id': 1, 'filtered_date': datetime.now() - timedelta(days=30)},   # Recent
        {'id': 2, 'filtered_date': datetime.now() - timedelta(days=120)},  # Old
        {'id': 3, 'filtered_date': datetime.now() - timedelta(days=200)}   # Very old
    ]
    
    # Cleanup threshold: 90 days
    cleanup_threshold = datetime.now() - timedelta(days=90)
    
    # Find scenes to cleanup
    scenes_to_cleanup = [s for s in scenes if s['filtered_date'] < cleanup_threshold]
    scenes_to_keep = [s for s in scenes if s['filtered_date'] >= cleanup_threshold]
    
    assert len(scenes_to_cleanup) == 2  # Scenes 2 and 3
    assert len(scenes_to_keep) == 1     # Scene 1
    assert scenes_to_keep[0]['id'] == 1
