#!/usr/bin/env python3
"""
WSGI entry point for Stash-Filter application.

This file is used by WSGI servers like Gunicorn to serve the application.
"""

import os
from app import create_app

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    # For development only - use gunicorn for production
    app.run(host='0.0.0.0', port=5000, debug=False)
