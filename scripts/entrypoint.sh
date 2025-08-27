#!/bin/bash

# Stash-Filter Docker Entrypoint Script
set -e

echo "Starting Stash-Filter application..."

# Set default database path if not provided
export DATABASE_PATH=${DATABASE_PATH:-/app/data/stash_filter.db}

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
if [ ! -f "$DATABASE_PATH" ]; then
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

# Run database migrations if migration system exists
if [ -f "/app/run_migration.py" ] && [ -d "/app/migrations" ]; then
    echo "Running database migrations..."
    
    # Get list of migration files and sort them
    migration_files=$(find /app/migrations -name "*.py" -type f ! -name "__*" | sort)
    
    for migration_file in $migration_files; do
        if [ -f "$migration_file" ]; then
            migration_name=$(basename "$migration_file" .py)
            echo "Checking migration: $migration_name"
            
            # Check if migration is needed and run it
            if ! python /app/run_migration.py "$migration_name" status 2>/dev/null | grep -q "APPLIED"; then
                echo "Running migration: $migration_name"
                python /app/run_migration.py "$migration_name" upgrade
                if [ $? -eq 0 ]; then
                    echo "Migration $migration_name completed successfully"
                else
                    echo "Migration $migration_name failed!"
                    exit 1
                fi
            else
                echo "Migration $migration_name already applied"
            fi
        fi
    done
    
    echo "Database migrations completed"
else
    echo "No migration system found, running basic schema creation..."
    python -c "
from app import create_app
from app.models import db
app = create_app()
with app.app_context():
    db.create_all()
    print('Basic schema creation completed')
"
fi

# Start cron daemon for scheduled tasks
echo "Starting cron daemon..."
cron

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