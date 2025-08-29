#!/usr/bin/env python3
"""
WSGI entry point for Stash-Filter Flask application
"""

import os
import sys
import json
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded environment variables from {env_path}")
except ImportError:
    print("python-dotenv not available, using system environment variables")

# Ensure critical environment variables are set
required_vars = {
    'STASH_URL': 'http://10.11.12.70:6969',
    'STASH_API_KEY': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiJjaEZyZXNoIiwiaWF0IjoxNzQ2OTkxNDQyLCJzdWIiOiJBUElLZXkifQ.xNuPPUxduQIC5F4q-IGF0eoi8mIP95QhtpnCz52aQUk',
    'WHISPARR_URL': 'http://10.11.12.77:6969',
    'WHISPARR_API_KEY': 'b3b0672869b54552ba1df30c24661f78',
    'STASHDB_URL': 'https://stashdb.org',
    'STASHDB_API_KEY': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiI5NzcxN2JjYi00MDhjLTQ0YTEtOTBkZS01MjNiNjdjZGYzZjMiLCJzdWIiOiJBUElLZXkiLCJpYXQiOjE3MjU5MTc1OTZ9.LL2Tb-5lYzEoILSYGL8_SITug6tTUc0ehm4bFQRneyU',
    'DATABASE_PATH': '/app/data/stash_filter.db',
    'FLASK_ENV': 'production'
}

for var, default_value in required_vars.items():
    if not os.environ.get(var):
        os.environ[var] = default_value
        print(f"Set default value for {var}")

print("Environment variables configured:")
for var in required_vars.keys():
    value = os.environ.get(var, 'NOT SET')
    # Mask API keys for security
    if 'API_KEY' in var and value != 'NOT SET':
        display_value = value[:20] + '...' if len(value) > 20 else value
    else:
        display_value = value
    print(f"  {var}: {display_value}")

from app.main import create_app

# Create the Flask application instance
application = create_app()

if __name__ == "__main__":
    # For development/testing
    application.run(host='0.0.0.0', port=5000, debug=False)

# Expose app under both names for compatibility
app = application
