#!/bin/bash

# Stash-Filter Docker Entrypoint Script

set -e

echo "Starting Stash-Filter application..."

# Check if data directory exists and create if not
if [ ! -d "/app/data" ]; then
    echo "Creating data directory..."
    mkdir -p /app/data
fi

# Check if logs directory exists and create if not  
if [ ! -d "/app/logs" ]; then
    echo "Creating logs directory..."
    mkdir -p /app/logs
fi

# Initialize database if it doesn't exist
if [ ! -f "/app/data/stash_filter.db" ]; then
    echo "Initializing database..."
    python -c "
from app import create_app
from app.models import db
app = create_app()
with app.app_context():
    db.create_all()
    print('Database initialized successfully')
"
fi

# Start cron daemon for scheduled tasks
echo "Starting cron daemon..."
cron

# Run database migrations if needed
echo "Running database migrations..."
python -c "
from app import create_app
from app.models import db
app = create_app()
with app.app_context():
    # Add any migration logic here if needed
    print('Database migrations completed')
"

# Test external connections on startup
echo "Testing external API connections..."
python -c "
import os
from app.services.stash_client import test_stash_connection
from app.services.stashdb_client import test_stashdb_connection
from app.services.whisparr_client import test_whisparr_connection

# Test Stash connection
try:
    if test_stash_connection():
        print('✓ Stash connection successful')
    else:
        print('✗ Stash connection failed')
except Exception as e:
    print(f'✗ Stash connection error: {e}')

# Test StashDB connection
try:
    if test_stashdb_connection():
        print('✓ StashDB connection successful')
    else:
        print('✗ StashDB connection failed')  
except Exception as e:
    print(f'✗ StashDB connection error: {e}')

# Test Whisparr connection (optional)
try:
    if os.getenv('WHISPARR_URL') and os.getenv('WHISPARR_API_KEY'):
        if test_whisparr_connection():
            print('✓ Whisparr connection successful')
        else:
            print('✗ Whisparr connection failed')
    else:
        print('- Whisparr not configured (optional)')
except Exception as e:
    print(f'✗ Whisparr connection error: {e}')
"

# Start the Flask application
echo "Starting Flask application..."
echo "Application will be available at http://localhost:5000"

# Use gunicorn for production, flask dev server for development
if [ "${FLASK_ENV}" = "development" ]; then
    echo "Running in development mode..."
    export FLASK_APP=app:create_app
    flask run --host=0.0.0.0 --port=5000
else
    echo "Running in production mode..."
    gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 60 wsgi:app
fi
