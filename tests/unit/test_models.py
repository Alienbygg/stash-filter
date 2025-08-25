"""
Unit tests for application models.
"""

import pytest
from datetime import datetime
from app.models import Performer, Studio, Scene, WantedScene, Config

def test_performer_creation(app, sample_performer_data):
    """Test creating a performer model."""
    with app.app_context():
        performer = Performer(**sample_performer_data)
        assert performer.name == "Test Performer"
        assert performer.stash_id == "1"
        assert performer.monitored == True
        assert len(performer.aliases) == 1
        
def test_performer_string_representation(app, sample_performer_data):
    """Test performer string representation."""
    with app.app_context():
        performer = Performer(**sample_performer_data)
        assert str(performer) == "Test Performer"

def test_studio_creation(app, sample_studio_data):
    """Test creating a studio model."""
    with app.app_context():
        studio = Studio(**sample_studio_data)
        assert studio.name == "Test Studio"
        assert studio.stash_id == "1"
        assert studio.monitored == True

def test_studio_string_representation(app, sample_studio_data):
    """Test studio string representation."""
    with app.app_context():
        studio = Studio(**sample_studio_data)
        assert str(studio) == "Test Studio"

def test_scene_creation(app, sample_scene_data):
    """Test creating a scene model."""
    with app.app_context():
        scene = Scene(**sample_scene_data)
        assert scene.title == "Test Scene Title"
        assert scene.duration == 1800
        assert scene.is_wanted == True
        assert scene.is_filtered == False

def test_scene_duration_minutes(app, sample_scene_data):
    """Test scene duration in minutes calculation."""
    with app.app_context():
        scene = Scene(**sample_scene_data)
        assert scene.duration_minutes == 30  # 1800 seconds = 30 minutes

def test_scene_filtering(app, sample_scene_data):
    """Test scene filtering logic."""
    with app.app_context():
        scene = Scene(**sample_scene_data)
        
        # Test filtering by unwanted categories
        scene.categories = ['anal']
        scene.filter_reason = 'Contains unwanted category: anal'
        scene.is_filtered = True
        
        assert scene.is_filtered == True
        assert 'anal' in scene.filter_reason

def test_wanted_scene_creation(app, sample_scene_data):
    """Test creating a wanted scene model."""
    with app.app_context():
        scene = Scene(**sample_scene_data)
        wanted = WantedScene(
            scene=scene,
            title=scene.title,
            performer_name="Test Performer",
            studio_name="Test Studio",
            release_date=datetime.strptime(scene.release_date, '%Y-%m-%d').date()
        )
        
        assert wanted.title == "Test Scene Title"
        assert wanted.status == "wanted"
        assert wanted.added_to_whisparr == False

def test_config_creation(app, sample_config_data):
    """Test creating a config model.""" 
    with app.app_context():
        config = Config(**sample_config_data)
        assert config.discovery_enabled == True
        assert config.max_scenes_per_check == 100
        assert 'anal' in config.unwanted_categories
        assert 'lesbian' in config.required_categories

def test_config_defaults(app):
    """Test config model defaults."""
    with app.app_context():
        config = Config()
        assert config.discovery_enabled == True
        assert config.discovery_frequency_hours == 24
        assert config.max_scenes_per_check == 100
        assert config.min_duration_minutes == 5
        assert config.max_duration_minutes == 300

def test_performer_monitoring_toggle(app, sample_performer_data):
    """Test toggling performer monitoring status."""
    with app.app_context():
        performer = Performer(**sample_performer_data)
        
        # Initially monitored
        assert performer.monitored == True
        
        # Toggle monitoring
        performer.monitored = False
        assert performer.monitored == False

def test_scene_relationships(app, sample_scene_data, sample_performer_data, sample_studio_data):
    """Test scene relationships with performer and studio."""
    with app.app_context():
        from app import db
        
        # Create performer and studio
        performer = Performer(**sample_performer_data)
        studio = Studio(**sample_studio_data) 
        db.session.add(performer)
        db.session.add(studio)
        db.session.commit()
        
        # Create scene with relationships
        scene_data = sample_scene_data.copy()
        scene_data['performer_id'] = performer.id
        scene_data['studio_id'] = studio.id
        
        scene = Scene(**scene_data)
        db.session.add(scene)
        db.session.commit()
        
        # Test relationships
        assert scene.performer == performer
        assert scene.studio == studio
        assert scene in performer.scenes
        assert scene in studio.scenes

def test_scene_duplicate_detection(app, sample_scene_data):
    """Test scene duplicate detection."""
    with app.app_context():
        from app import db
        
        # Create first scene
        scene1 = Scene(**sample_scene_data)
        db.session.add(scene1)
        db.session.commit()
        
        # Try to create duplicate scene with same stashdb_id
        scene2_data = sample_scene_data.copy()
        scene2 = Scene(**scene2_data)
        
        # This should be caught by unique constraint
        db.session.add(scene2)
        with pytest.raises(Exception):  # SQLAlchemy IntegrityError
            db.session.commit()

def test_config_json_fields(app, sample_config_data):
    """Test config JSON field serialization."""
    with app.app_context():
        config = Config(**sample_config_data)
        
        # Test that JSON fields are properly stored
        assert isinstance(config.unwanted_categories, list)
        assert isinstance(config.required_categories, list)
        assert 'anal' in config.unwanted_categories
        assert 'lesbian' in config.required_categories
