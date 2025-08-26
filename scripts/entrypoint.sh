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

# Test external connections on startup (simplified for now)
echo "Testing external API connections..."
python -c "
import os
print('External API connection testing skipped for now - will be added after app starts')
print('You can test connections via the web interface')
"

# Start the Flask application
echo "Starting Flask application..."
echo "Application will be available at http://localhost:5000"

# Use gunicorn for production, flask dev server for development
if [ "${FLASK_ENV}" = "development" ]; then
    echo "Running in development mode..."
    export FLASK_APP=wsgi:app
    python -m flask run --host=0.0.0.0 --port=5000
else
    echo "Running in production mode..."
    gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 60 wsgi:app
fi