"""
Flask routes for Stash-Filter application.
"""

from flask import Blueprint

# Import route modules
from .main import main_bp
from .api import api_bp
from .health import health_bp

# Export blueprints for registration
__all__ = ['main_bp', 'api_bp', 'health_bp']
