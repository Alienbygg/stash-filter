from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import logging
from datetime import datetime

# Import custom modules
from .models import db, Performer, Studio, Scene, WantedScene, Config
from .stash_api import StashAPI
from .stashdb_api import StashDBAPI
from .whisparr_api import WhisparrAPI
from .scheduler import setup_scheduler

def create_app():
    # Set template and static folders relative to project root
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.environ.get('DATABASE_PATH', '/app/data/stash_filter.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, os.environ.get('LOG_LEVEL', 'INFO')),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize APIs
    stash_api = StashAPI()
    stashdb_api = StashDBAPI()
    whisparr_api = WhisparrAPI()
    
    # Routes

