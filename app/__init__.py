"""
Stash-Filter Flask Application

A Docker application for automatically discovering new scenes from favorite
performers and studios using Stash, StashDB, and Whisparr integration.
"""

import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Initialize extensions
db = SQLAlchemy()

# Application version
__version__ = "1.0.0"

def create_app(config_name=None):
    """
    Flask application factory.
    
    Args:
        config_name: Configuration name (development, production, testing)
        
    Returns:
        Flask: Configured Flask application instance
    """
    # Load environment variables
    load_dotenv()
    
    # Create Flask app
    app = Flask(__name__)
    
    # Configure app
    configure_app(app, config_name)
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Configure logging
    configure_logging(app)
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.error(f"Failed to create database tables: {str(e)}")
    
    return app

def configure_app(app, config_name=None):
    """Configure Flask application."""
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Database configuration  
    database_path = os.getenv('DATABASE_PATH', '/app/data/stash_filter.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
    
    # Environment-specific configuration
    flask_env = os.getenv('FLASK_ENV', 'production')
    
    if flask_env == 'development':
        app.config['DEBUG'] = True
        app.config['TESTING'] = False
    elif flask_env == 'testing':
        app.config['DEBUG'] = False
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    else:
        app.config['DEBUG'] = False
        app.config['TESTING'] = False

def register_blueprints(app):
    """Register Flask blueprints."""
    
    # Import blueprints
    from app.routes.main import main_bp
    from app.routes.api import api_bp
    from app.routes.health import health_bp
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(health_bp)

def configure_logging(app):
    """Configure application logging."""
    
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Set log level
    numeric_level = getattr(logging, log_level, logging.INFO)
    logging.basicConfig(level=numeric_level, format=log_format)
    
    # Configure Flask app logger
    app.logger.setLevel(numeric_level)
    
    # Log startup message
    app.logger.info(f"Stash-Filter v{__version__} starting up")
    app.logger.info(f"Environment: {os.getenv('FLASK_ENV', 'production')}")
    app.logger.info(f"Database: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
