# Stash-Filter Docker Application

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://hub.docker.com)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)

## Overview
Stash-Filter is a Docker application designed to automatically discover new scenes for your favorite performers and studios. It integrates with Stash, StashDB, and Whisparr to provide a comprehensive content discovery and management solution.

## Features
- 🔍 **Daily Content Discovery**: Automatically checks for new scenes from favorite performers and studios
- 🎯 **Smart Filtering**: Filters out scenes you already have and unwanted categories
- 💾 **Database Tracking**: Maintains a local database of discovered scenes and monitoring status
- 🌐 **Web Interface**: Easy-to-use interface to manage monitored performers and studios
- 📥 **Whisparr Integration**: Automatically adds wanted scenes to Whisparr for download
- 🐳 **Docker Ready**: Full Docker containerization with Unraid support
- 📊 **Health Monitoring**: Built-in health checks and logging

## Architecture
- **Backend**: Python Flask application
- **Database**: SQLite for local data storage
- **Frontend**: Web-based interface with responsive design
- **Scheduler**: Cron-based daily content checks
- **APIs**: Integration with Stash, StashDB, and Whisparr

## Quick Start

### Docker Compose (Recommended)
```bash
git clone https://github.com/Alienbygg/stash-filter.git
cd stash-filter
cp .env.example .env
# Edit .env with your configuration
docker-compose up -d
```

### Manual Docker Build
```bash
docker build -t stash-filter .
docker run -d --name stash-filter -p 5000:5000 -v $(pwd)/data:/app/data stash-filter
```

### Unraid Installation
1. Go to **Docker** tab in Unraid
2. Click **Add Container**
3. Use the template: `https://raw.githubusercontent.com/Alienbygg/stash-filter/main/unraid-template.xml`
4. Configure your settings and apply

## Configuration

### Environment Variables
Copy `.env.example` to `.env` and configure the following:

| Variable | Description | Example |
|----------|-------------|---------|
| `STASH_URL` | Your Stash server URL | `http://192.168.1.100:9999` |
| `STASH_API_KEY` | Stash API key | `your-stash-api-key` |
| `WHISPARR_URL` | Whisparr server URL (optional) | `http://192.168.1.100:6969` |
| `WHISPARR_API_KEY` | Whisparr API key (optional) | `your-whisparr-api-key` |
| `STASHDB_API_KEY` | StashDB API key (optional) | `your-stashdb-api-key` |

### First Run
1. Access the web interface at `http://your-server-ip:5000`
2. Navigate to Settings to configure your API connections
3. Add your favorite performers and studios
4. Set unwanted categories to filter out
5. The application will automatically run daily checks

## Project Structure
```
stash-filter/
├── app/                    # Main application code
│   ├── __init__.py        # Flask app initialization
│   ├── routes/            # Web routes
│   ├── models/            # Database models
│   ├── services/          # Business logic
│   └── utils/             # Utility functions
├── config/                # Configuration files
├── database/              # Database schema and migrations
├── static/                # Web assets (CSS, JS, images)
├── templates/             # HTML templates
├── scripts/               # Deployment and utility scripts
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker build instructions
├── docker-compose.yml    # Docker Compose configuration
├── .env.example          # Environment variables example
├── unraid-template.xml   # Unraid Docker template
└── README.md            # This file
```

## API Documentation
See [API.md](API.md) for detailed API endpoint documentation.

## Development
See [DEVELOPMENT.md](DEVELOPMENT.md) for development setup and contribution guidelines.

## Screenshots

### Main Dashboard
![Dashboard](screenshots/dashboard.png)

### Settings Page
![Settings](screenshots/settings.png)

## Support

- 📖 **Documentation**: Check the [docs](docs/) folder
- 🐛 **Issues**: [GitHub Issues](https://github.com/Alienbygg/stash-filter/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/Alienbygg/stash-filter/discussions)

## Contributing
Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- [Stash](https://github.com/stashapp/stash) - The amazing media organizer
- [StashDB](https://stashdb.org) - Community database
- [Whisparr](https://github.com/Whisparr/Whisparr) - Adult content management
# Docker login fix
