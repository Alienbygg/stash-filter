"""
Database models for Stash-Filter application.
"""

from datetime import datetime, date
from app import db
import json


class Performer(db.Model):
    """Performer model for tracking favorite performers."""
    
    __tablename__ = 'performers'
    
    id = db.Column(db.Integer, primary_key=True)
    stash_id = db.Column(db.String(50), unique=True, nullable=False)
    stashdb_id = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(255), nullable=False)
    aliases = db.Column(db.Text)  # JSON array of aliases
    monitored = db.Column(db.Boolean, default=True, nullable=False)
    last_checked = db.Column(db.DateTime)
    created_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    scenes = db.relationship('Scene', backref='performer', lazy='dynamic', 
                           foreign_keys='Scene.performer_id')
    
    def __repr__(self):
        return f'<Performer {self.name}>'
    
    def __str__(self):
        return self.name
    
    @property
    def aliases_list(self):
        """Get aliases as a list."""
        if self.aliases:
            try:
                return json.loads(self.aliases)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    @aliases_list.setter
    def aliases_list(self, value):
        """Set aliases from a list."""
        if isinstance(value, list):
            self.aliases = json.dumps(value)
        else:
            self.aliases = json.dumps([])
    
    def to_dict(self):
        """Convert performer to dictionary."""
        return {
            'id': self.id,
            'stash_id': self.stash_id,
            'stashdb_id': self.stashdb_id,
            'name': self.name,
            'aliases': self.aliases_list,
            'monitored': self.monitored,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None,
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }


class Studio(db.Model):
    """Studio model for tracking favorite studios."""
    
    __tablename__ = 'studios'
    
    id = db.Column(db.Integer, primary_key=True)
    stash_id = db.Column(db.String(50), unique=True, nullable=False)
    stashdb_id = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(255), nullable=False)
    parent_studio = db.Column(db.String(255))
    network = db.Column(db.String(255))
    monitored = db.Column(db.Boolean, default=True, nullable=False)
    last_checked = db.Column(db.DateTime)
    created_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    scenes = db.relationship('Scene', backref='studio', lazy='dynamic',
                           foreign_keys='Scene.studio_id')
    
    def __repr__(self):
        return f'<Studio {self.name}>'
    
    def __str__(self):
        return self.name
    
    def to_dict(self):
        """Convert studio to dictionary."""
        return {
            'id': self.id,
            'stash_id': self.stash_id,
            'stashdb_id': self.stashdb_id,
            'name': self.name,
            'parent_studio': self.parent_studio,
            'network': self.network,
            'monitored': self.monitored,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None,
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }


class Scene(db.Model):
    """Scene model for discovered scenes."""
    
    __tablename__ = 'scenes'
    
    id = db.Column(db.Integer, primary_key=True)
    stashdb_id = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String(500), nullable=False)
    release_date = db.Column(db.String(20))  # Store as string for flexibility
    duration = db.Column(db.Integer)  # Duration in seconds
    tags = db.Column(db.Text)  # JSON array of tags
    categories = db.Column(db.Text)  # JSON array of categories
    rating = db.Column(db.Float)
    
    # Foreign keys
    performer_id = db.Column(db.Integer, db.ForeignKey('performers.id'))
    studio_id = db.Column(db.Integer, db.ForeignKey('studios.id'))
    
    # Status flags
    is_owned = db.Column(db.Boolean, default=False, nullable=False)
    is_wanted = db.Column(db.Boolean, default=True, nullable=False)
    is_filtered = db.Column(db.Boolean, default=False, nullable=False)
    filter_reason = db.Column(db.String(255))
    
    # Timestamps
    discovered_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    wanted_scene = db.relationship('WantedScene', backref='scene', uselist=False)
    
    def __repr__(self):
        return f'<Scene {self.title}>'
    
    def __str__(self):
        return self.title
    
    @property
    def duration_minutes(self):
        """Get duration in minutes."""
        if self.duration:
            return round(self.duration / 60)
        return None
    
    @property
    def tags_list(self):
        """Get tags as a list."""
        if self.tags:
            try:
                return json.loads(self.tags)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    @tags_list.setter
    def tags_list(self, value):
        """Set tags from a list."""
        if isinstance(value, list):
            self.tags = json.dumps(value)
        else:
            self.tags = json.dumps([])
    
    @property
    def categories_list(self):
        """Get categories as a list."""
        if self.categories:
            try:
                return json.loads(self.categories)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    @categories_list.setter
    def categories_list(self, value):
        """Set categories from a list."""
        if isinstance(value, list):
            self.categories = json.dumps(value)
        else:
            self.categories = json.dumps([])
    
    def to_dict(self):
        """Convert scene to dictionary."""
        return {
            'id': self.id,
            'stashdb_id': self.stashdb_id,
            'title': self.title,
            'release_date': self.release_date,
            'duration': self.duration,
            'duration_minutes': self.duration_minutes,
            'tags': self.tags_list,
            'categories': self.categories_list,
            'rating': self.rating,
            'performer_id': self.performer_id,
            'performer_name': self.performer.name if self.performer else None,
            'studio_id': self.studio_id,
            'studio_name': self.studio.name if self.studio else None,
            'is_owned': self.is_owned,
            'is_wanted': self.is_wanted,
            'is_filtered': self.is_filtered,
            'filter_reason': self.filter_reason,
            'discovered_date': self.discovered_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }


class WantedScene(db.Model):
    """Wanted scenes tracking for download management."""
    
    __tablename__ = 'wanted_scenes'
    
    id = db.Column(db.Integer, primary_key=True)
    scene_id = db.Column(db.Integer, db.ForeignKey('scenes.id'), nullable=False)
    whisparr_id = db.Column(db.String(100))  # Whisparr movie ID
    
    # Scene information for quick access
    title = db.Column(db.String(500), nullable=False)
    performer_name = db.Column(db.String(255))
    studio_name = db.Column(db.String(255))
    release_date = db.Column(db.Date)
    
    # Download status
    status = db.Column(db.String(50), default='wanted', nullable=False)
    added_to_whisparr = db.Column(db.Boolean, default=False, nullable=False)
    download_status = db.Column(db.String(50))  # downloading, completed, failed, etc.
    
    # Timestamps
    added_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    whisparr_added_date = db.Column(db.DateTime)
    status_updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<WantedScene {self.title}>'
    
    def __str__(self):
        return self.title
    
    def to_dict(self):
        """Convert wanted scene to dictionary."""
        return {
            'id': self.id,
            'scene_id': self.scene_id,
            'whisparr_id': self.whisparr_id,
            'title': self.title,
            'performer_name': self.performer_name,
            'studio_name': self.studio_name,
            'release_date': self.release_date.isoformat() if self.release_date else None,
            'status': self.status,
            'added_to_whisparr': self.added_to_whisparr,
            'download_status': self.download_status,
            'added_date': self.added_date.isoformat(),
            'whisparr_added_date': self.whisparr_added_date.isoformat() if self.whisparr_added_date else None,
            'status_updated_date': self.status_updated_date.isoformat()
        }


class Config(db.Model):
    """Application configuration settings."""
    
    __tablename__ = 'config'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Content filtering
    unwanted_categories = db.Column(db.Text)  # JSON array
    required_categories = db.Column(db.Text)  # JSON array
    min_duration_minutes = db.Column(db.Integer, default=5)
    max_duration_minutes = db.Column(db.Integer, default=300)
    min_rating = db.Column(db.Float, default=0.0)
    
    # Discovery settings
    discovery_enabled = db.Column(db.Boolean, default=True, nullable=False)
    discovery_frequency_hours = db.Column(db.Integer, default=24)
    max_scenes_per_check = db.Column(db.Integer, default=100)
    auto_add_to_whisparr = db.Column(db.Boolean, default=False)
    
    # Whisparr settings
    whisparr_quality_profile = db.Column(db.String(100), default='HD')
    whisparr_root_folder = db.Column(db.String(255))
    
    # Performance settings
    concurrent_requests = db.Column(db.Integer, default=3)
    request_timeout = db.Column(db.Integer, default=30)
    rate_limit_delay = db.Column(db.Integer, default=1)
    
    # Timestamps
    created_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Config {self.id}>'
    
    @property
    def unwanted_categories_list(self):
        """Get unwanted categories as a list."""
        if self.unwanted_categories:
            try:
                return json.loads(self.unwanted_categories)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    @unwanted_categories_list.setter
    def unwanted_categories_list(self, value):
        """Set unwanted categories from a list."""
        if isinstance(value, list):
            self.unwanted_categories = json.dumps(value)
        else:
            self.unwanted_categories = json.dumps([])
    
    @property
    def required_categories_list(self):
        """Get required categories as a list."""
        if self.required_categories:
            try:
                return json.loads(self.required_categories)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    @required_categories_list.setter
    def required_categories_list(self, value):
        """Set required categories from a list."""
        if isinstance(value, list):
            self.required_categories = json.dumps(value)
        else:
            self.required_categories = json.dumps([])
    
    def to_dict(self):
        """Convert config to dictionary."""
        return {
            'id': self.id,
            'unwanted_categories': self.unwanted_categories_list,
            'required_categories': self.required_categories_list,
            'min_duration_minutes': self.min_duration_minutes,
            'max_duration_minutes': self.max_duration_minutes,
            'min_rating': self.min_rating,
            'discovery_enabled': self.discovery_enabled,
            'discovery_frequency_hours': self.discovery_frequency_hours,
            'max_scenes_per_check': self.max_scenes_per_check,
            'auto_add_to_whisparr': self.auto_add_to_whisparr,
            'whisparr_quality_profile': self.whisparr_quality_profile,
            'whisparr_root_folder': self.whisparr_root_folder,
            'concurrent_requests': self.concurrent_requests,
            'request_timeout': self.request_timeout,
            'rate_limit_delay': self.rate_limit_delay,
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }


class DiscoveryLog(db.Model):
    """Log entries for discovery runs."""
    
    __tablename__ = 'discovery_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.String(100), nullable=False)  # UUID for each discovery run
    
    # Run statistics
    total_performers = db.Column(db.Integer, default=0)
    total_studios = db.Column(db.Integer, default=0)
    scenes_discovered = db.Column(db.Integer, default=0)
    scenes_filtered = db.Column(db.Integer, default=0)
    scenes_added_wanted = db.Column(db.Integer, default=0)
    scenes_added_whisparr = db.Column(db.Integer, default=0)
    
    # Run details
    status = db.Column(db.String(50), default='running', nullable=False)  # running, completed, failed
    error_message = db.Column(db.Text)
    duration_seconds = db.Column(db.Integer)
    
    # Timestamps
    started_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_date = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<DiscoveryLog {self.run_id}>'
    
    def to_dict(self):
        """Convert discovery log to dictionary."""
        return {
            'id': self.id,
            'run_id': self.run_id,
            'total_performers': self.total_performers,
            'total_studios': self.total_studios,
            'scenes_discovered': self.scenes_discovered,
            'scenes_filtered': self.scenes_filtered,
            'scenes_added_wanted': self.scenes_added_wanted,
            'scenes_added_whisparr': self.scenes_added_whisparr,
            'status': self.status,
            'error_message': self.error_message,
            'duration_seconds': self.duration_seconds,
            'started_date': self.started_date.isoformat(),
            'completed_date': self.completed_date.isoformat() if self.completed_date else None
        }


class FilteredScene(db.Model):
    """Model for tracking scenes that were filtered out during discovery."""
    
    __tablename__ = 'filtered_scenes'
    
    id = db.Column(db.Integer, primary_key=True)
    stash_id = db.Column(db.String(50))
    stashdb_id = db.Column(db.String(100))
    title = db.Column(db.String(500), nullable=False)
    performers = db.Column(db.Text)  # JSON array of performer names
    studio = db.Column(db.String(200))
    tags = db.Column(db.Text)  # JSON array of tags
    duration = db.Column(db.Integer)  # Duration in seconds
    release_date = db.Column(db.String(20))
    
    # Filter information
    filter_reason = db.Column(db.String(100), nullable=False)
    filter_category = db.Column(db.String(50), nullable=False)
    filter_details = db.Column(db.Text)  # JSON with detailed filter info
    
    # Scene URLs and metadata
    scene_url = db.Column(db.String(500))
    thumbnail_url = db.Column(db.String(500))
    
    # Exception tracking
    is_exception = db.Column(db.Boolean, default=False, nullable=False)
    exception_date = db.Column(db.DateTime)
    exception_reason = db.Column(db.String(500))
    
    # Timestamps
    filtered_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    exceptions = db.relationship('FilterException', backref='filtered_scene', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<FilteredScene {self.title}>'
    
    def __str__(self):
        return self.title
    
    @property
    def performers_list(self):
        """Get performers as a list."""
        if self.performers:
            try:
                return json.loads(self.performers)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    @performers_list.setter
    def performers_list(self, value):
        """Set performers from a list."""
        if isinstance(value, list):
            self.performers = json.dumps(value)
        else:
            self.performers = json.dumps([])
    
    @property
    def tags_list(self):
        """Get tags as a list."""
        if self.tags:
            try:
                return json.loads(self.tags)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    @tags_list.setter
    def tags_list(self, value):
        """Set tags from a list."""
        if isinstance(value, list):
            self.tags = json.dumps(value)
        else:
            self.tags = json.dumps([])
    
    @property
    def filter_details_dict(self):
        """Get filter details as a dictionary."""
        if self.filter_details:
            try:
                return json.loads(self.filter_details)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    @filter_details_dict.setter
    def filter_details_dict(self, value):
        """Set filter details from a dictionary."""
        if isinstance(value, dict):
            self.filter_details = json.dumps(value)
        else:
            self.filter_details = json.dumps({})
    
    @property
    def duration_minutes(self):
        """Get duration in minutes."""
        if self.duration:
            return round(self.duration / 60)
        return None
    
    @property
    def has_active_exception(self):
        """Check if scene has an active exception."""
        from datetime import datetime
        for exception in self.exceptions:
            if exception.is_active and (not exception.expires_at or exception.expires_at > datetime.utcnow()):
                return True
        return False
    
    def to_dict(self):
        """Convert filtered scene to dictionary."""
        return {
            'id': self.id,
            'stash_id': self.stash_id,
            'stashdb_id': self.stashdb_id,
            'title': self.title,
            'performers': self.performers_list,
            'studio': self.studio,
            'tags': self.tags_list,
            'duration': self.duration,
            'duration_minutes': self.duration_minutes,
            'release_date': self.release_date,
            'filter_reason': self.filter_reason,
            'filter_category': self.filter_category,
            'filter_details': self.filter_details_dict,
            'scene_url': self.scene_url,
            'thumbnail_url': self.thumbnail_url,
            'is_exception': self.is_exception,
            'has_active_exception': self.has_active_exception,
            'exception_date': self.exception_date.isoformat() if self.exception_date else None,
            'exception_reason': self.exception_reason,
            'filtered_date': self.filtered_date.isoformat(),
            'created_at': self.created_at.isoformat()
        }


class FilterException(db.Model):
    """Model for tracking exceptions to filtered scenes."""
    
    __tablename__ = 'filter_exceptions'
    
    id = db.Column(db.Integer, primary_key=True)
    filtered_scene_id = db.Column(db.Integer, db.ForeignKey('filtered_scenes.id'), nullable=False)
    
    # Exception configuration
    exception_type = db.Column(db.String(50), nullable=False)  # 'permanent', 'temporary', 'one-time'
    reason = db.Column(db.String(500))
    created_by = db.Column(db.String(100), default='user', nullable=False)
    
    # Expiration settings
    expires_at = db.Column(db.DateTime)  # For temporary exceptions
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Usage tracking
    times_used = db.Column(db.Integer, default=0, nullable=False)
    last_used_date = db.Column(db.DateTime)
    
    # Additional settings
    auto_add_to_whisparr = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<FilterException {self.id} - {self.exception_type}>'
    
    @property
    def is_expired(self):
        """Check if exception has expired."""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    @property
    def is_valid(self):
        """Check if exception is valid (active and not expired)."""
        return self.is_active and not self.is_expired
    
    def use_exception(self):
        """Mark exception as used and update usage stats."""
        self.times_used += 1
        self.last_used_date = datetime.utcnow()
        
        # For one-time exceptions, deactivate after use
        if self.exception_type == 'one-time':
            self.is_active = False
    
    def to_dict(self):
        """Convert filter exception to dictionary."""
        return {
            'id': self.id,
            'filtered_scene_id': self.filtered_scene_id,
            'exception_type': self.exception_type,
            'reason': self.reason,
            'created_by': self.created_by,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'is_expired': self.is_expired,
            'is_valid': self.is_valid,
            'times_used': self.times_used,
            'last_used_date': self.last_used_date.isoformat() if self.last_used_date else None,
            'auto_add_to_whisparr': self.auto_add_to_whisparr,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
