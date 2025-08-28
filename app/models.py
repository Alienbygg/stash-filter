from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Performer(db.Model):
    """Model for favorite performers"""
    __tablename__ = 'performers'
    
    id = db.Column(db.Integer, primary_key=True)
    stash_id = db.Column(db.String(50), unique=False, nullable=True)  # Can be null for manual additions
    stashdb_id = db.Column(db.String(50), unique=True, nullable=True)
    name = db.Column(db.String(200), nullable=False)
    aliases = db.Column(db.Text)  # JSON string of aliases
    monitored = db.Column(db.Boolean, default=True)
    last_checked = db.Column(db.DateTime, default=datetime.utcnow)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    scenes = db.relationship('Scene', backref='performer', lazy=True)
    
    def __repr__(self):
        return f'<Performer {self.name}>'
    
    def get_aliases(self):
        """Get aliases as list"""
        if self.aliases:
            try:
                return json.loads(self.aliases)
            except:
                return []
        return []
    
    def set_aliases(self, aliases_list):
        """Set aliases from list"""
        self.aliases = json.dumps(aliases_list) if aliases_list else None

class Studio(db.Model):
    """Model for favorite studios"""
    __tablename__ = 'studios'
    
    id = db.Column(db.Integer, primary_key=True)
    stash_id = db.Column(db.String(50), unique=False, nullable=True)  # Can be null for manual additions
    stashdb_id = db.Column(db.String(50), unique=True, nullable=True)
    name = db.Column(db.String(200), nullable=False)
    parent_studio = db.Column(db.String(200), nullable=True)
    monitored = db.Column(db.Boolean, default=True)
    last_checked = db.Column(db.DateTime, default=datetime.utcnow)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    scenes = db.relationship('Scene', backref='studio', lazy=True)
    
    def __repr__(self):
        return f'<Studio {self.name}>'

class Scene(db.Model):
    """Model for discovered scenes"""
    __tablename__ = 'scenes'
    
    id = db.Column(db.Integer, primary_key=True)
    stashdb_id = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(500), nullable=False)
    release_date = db.Column(db.Date, nullable=True)
    duration = db.Column(db.Integer, nullable=True)  # in seconds
    tags = db.Column(db.Text)  # JSON string of tags
    categories = db.Column(db.Text)  # JSON string of categories
    
    # Foreign keys
    performer_id = db.Column(db.Integer, db.ForeignKey('performers.id'), nullable=True)
    studio_id = db.Column(db.Integer, db.ForeignKey('studios.id'), nullable=True)
    
    # Status tracking
    is_owned = db.Column(db.Boolean, default=False)
    is_wanted = db.Column(db.Boolean, default=False)
    is_filtered = db.Column(db.Boolean, default=False)  # Filtered out by category rules
    filter_reason = db.Column(db.String(500))  # Why it was filtered
    
    # Timestamps
    discovered_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Scene {self.title}>'
    
    def get_tags(self):
        """Get tags as list"""
        if self.tags:
            try:
                return json.loads(self.tags)
            except:
                return []
        return []
    
    def set_tags(self, tags_list):
        """Set tags from list"""
        self.tags = json.dumps(tags_list) if tags_list else None
    
    def get_categories(self):
        """Get categories as list"""
        if self.categories:
            try:
                return json.loads(self.categories)
            except:
                return []
        return []
    
    def set_categories(self, categories_list):
        """Set categories from list"""
        self.categories = json.dumps(categories_list) if categories_list else None

class WantedScene(db.Model):
    """Model for scenes wanted in Whisparr"""
    __tablename__ = 'wanted_scenes'
    __table_args__ = (db.UniqueConstraint('scene_id', name='uq_wanted_scenes_scene_id'),)
    
    id = db.Column(db.Integer, primary_key=True)
    scene_id = db.Column(db.Integer, db.ForeignKey('scenes.id'), nullable=False)
    whisparr_id = db.Column(db.String(50), nullable=True)  # ID in Whisparr
    title = db.Column(db.String(500), nullable=False)
    performer_name = db.Column(db.String(200), nullable=True)
    studio_name = db.Column(db.String(200), nullable=True)
    release_date = db.Column(db.Date, nullable=True)
    
    # Status
    status = db.Column(db.String(50), default='wanted')  # wanted, requested, downloaded, failed
    added_to_whisparr = db.Column(db.Boolean, default=False)
    download_status = db.Column(db.String(100), nullable=True)
    
    # Timestamps
    added_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    scene = db.relationship('Scene', backref='wanted_entry', lazy=True)
    
    def __repr__(self):
        return f'<WantedScene {self.title}>'

class Config(db.Model):
    """Model for application configuration"""
    __tablename__ = 'config'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Category filters (JSON strings)
    unwanted_categories = db.Column(db.Text, default='[]')  # Categories to filter out
    required_categories = db.Column(db.Text, default='[]')  # Categories that must be present
    
    # Discovery settings
    discovery_enabled = db.Column(db.Boolean, default=True)
    discovery_frequency_hours = db.Column(db.Integer, default=24)
    max_scenes_per_check = db.Column(db.Integer, default=100)
    
    # Quality preferences
    min_duration_minutes = db.Column(db.Integer, default=0)
    max_duration_minutes = db.Column(db.Integer, default=0)  # 0 = no limit
    
    # Whisparr integration
    auto_add_to_whisparr = db.Column(db.Boolean, default=True)
    whisparr_quality_profile = db.Column(db.String(100), default='Any')
    
    # Timestamps
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_unwanted_categories(self):
        """Get unwanted categories as list"""
        try:
            return json.loads(self.unwanted_categories) if self.unwanted_categories else []
        except:
            return []
    
    def set_unwanted_categories(self, categories_list):
        """Set unwanted categories from list"""
        self.unwanted_categories = json.dumps(categories_list) if categories_list else '[]'
    
    def get_required_categories(self):
        """Get required categories as list"""
        try:
            return json.loads(self.required_categories) if self.required_categories else []
        except:
            return []
    
    def set_required_categories(self, categories_list):
        """Set required categories from list"""
        self.required_categories = json.dumps(categories_list) if categories_list else '[]'
    
    @staticmethod
    def get_config():
        """Get the configuration instance (creates one if none exists)"""
        config = Config.query.first()
        if not config:
            config = Config()
            db.session.add(config)
            db.session.commit()
        return config
    
    def __repr__(self):
        return f'<Config id={self.id}>'

class LogEntry(db.Model):
    """Model for application logs"""
    __tablename__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(20), nullable=False)  # INFO, WARNING, ERROR
    message = db.Column(db.Text, nullable=False)
    module = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<LogEntry {self.level}: {self.message[:50]}...>'

class FilteredScene(db.Model):
    """Model for scenes that were filtered out"""
    __tablename__ = 'filtered_scenes'
    
    id = db.Column(db.Integer, primary_key=True)
    stash_id = db.Column(db.String(50), nullable=True)
    stashdb_id = db.Column(db.String(100), nullable=True) 
    title = db.Column(db.String(500), nullable=False)
    performers = db.Column(db.Text)  # JSON string
    studio = db.Column(db.String(200), nullable=True)
    tags = db.Column(db.Text)  # JSON string
    duration = db.Column(db.Integer, nullable=True)
    release_date = db.Column(db.String(20), nullable=True)
    filter_reason = db.Column(db.String(100), nullable=False)
    filter_category = db.Column(db.String(50), nullable=False) 
    filter_details = db.Column(db.Text, nullable=True)
    scene_url = db.Column(db.String(500), nullable=True)
    thumbnail_url = db.Column(db.String(500), nullable=True)
    is_exception = db.Column(db.Boolean, default=False, nullable=False)
    exception_date = db.Column(db.DateTime, nullable=True)
    exception_reason = db.Column(db.String(500), nullable=True)
    filtered_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    exceptions = db.relationship('FilterException', backref='filtered_scene', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<FilteredScene {self.title}>'
    
    def get_performers(self):
        """Get performers as list"""
        if self.performers:
            try:
                return json.loads(self.performers)
            except:
                return []
        return []
    
    def set_performers(self, performers_list):
        """Set performers from list"""
        self.performers = json.dumps(performers_list) if performers_list else None
    
    def get_tags(self):
        """Get tags as list"""
        if self.tags:
            try:
                return json.loads(self.tags)
            except:
                return []
        return []
    
    def set_tags(self, tags_list):
        """Set tags from list"""
        self.tags = json.dumps(tags_list) if tags_list else None

class FilterException(db.Model):
    """Model for exceptions to filtering rules"""
    __tablename__ = 'filter_exceptions'
    
    id = db.Column(db.Integer, primary_key=True)
    filtered_scene_id = db.Column(db.Integer, db.ForeignKey('filtered_scenes.id'), nullable=False)
    exception_type = db.Column(db.String(50), nullable=False)  # 'permanent', 'temporary', 'conditional'
    reason = db.Column(db.String(500), nullable=True)
    created_by = db.Column(db.String(100), default='user', nullable=False)
    expires_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    times_used = db.Column(db.Integer, default=0, nullable=False)
    last_used_date = db.Column(db.DateTime, nullable=True)
    auto_add_to_whisparr = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<FilterException {self.exception_type} for {self.filtered_scene_id}>'
    
    def is_expired(self):
        """Check if this exception has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
