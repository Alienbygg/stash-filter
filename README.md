# Stash-Filter Docker Application

## Overview
Stash-Filter is a Docker application designed to automatically find new scenes for your favorite performers and studios. It integrates with Stash, StashDB, and Whisparr to provide a comprehensive content discovery and management solution.

## Features
- **Daily Content Discovery**: Automatically checks for new scenes from favorite performers and studios
- **Smart Filtering**: Filters out scenes you already have and unwanted categories
- **Database Tracking**: Maintains a local database of discovered scenes and monitoring status
- **Web Interface**: Easy-to-use interface to manage monitored performers and studios
- **Whisparr Integration**: Automatically adds wanted scenes to Whisparr for download

## Architecture
- **Backend**: Python Flask application
- **Database**: SQLite for local data storage
- **Frontend**: Web-based interface
- **Scheduler**: Cron-based daily content checks
- **APIs**: Integration with Stash, StashDB, and Whisparr

## Configuration
The application uses the following services:
- **Stash**: http://10.11.12.70:6969
- **Whisparr**: http://10.11.12.77:6969  
- **StashDB**: https://stashdb.org/

## Quick Start
1. Build the Docker container: `docker-compose up -d`
2. Access the web interface at: `http://10.11.12.70:5000`
3. Configure your favorite performers and studios
4. Set unwanted categories to filter out
5. The application will run daily checks automatically

## Project Structure
```
stash-filter/
├── app/                    # Main application code
├── config/                 # Configuration files
├── database/              # Database schema and migrations
├── static/                # Web assets (CSS, JS)
├── templates/             # HTML templates
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker build instructions
├── docker-compose.yml    # Docker Compose configuration
└── README.md            # This file
```

## Development
See DEVELOPMENT.md for detailed development instructions.

## API Documentation
See API.md for API endpoint documentation.
