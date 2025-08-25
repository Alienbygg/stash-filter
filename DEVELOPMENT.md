# Development Guide

## Prerequisites
- Python 3.11+
- Docker and Docker Compose
- Git
- A running Stash instance for testing

## Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/stash-filter.git
cd stash-filter
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration
```bash
cp .env.example .env
# Edit .env with your development settings
```

### 5. Initialize Database
```bash
python -c "from app import create_app; create_app().app_context().push(); from app.models import db; db.create_all()"
```

### 6. Run Development Server
```bash
export FLASK_APP=app
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

## Development with Docker

### Build Development Image
```bash
docker build -t stash-filter:dev .
```

### Run with Docker Compose
```bash
docker-compose -f docker-compose.dev.yml up -d
```

### View Logs
```bash
docker-compose logs -f stash-filter
```

## Testing

### Run Tests
```bash
pytest tests/
```

### Run with Coverage
```bash
pytest --cov=app tests/
```

### Integration Tests
```bash
pytest tests/integration/ -v
```

## Code Quality

### Format Code
```bash
black app/ tests/
```

### Lint Code  
```bash
flake8 app/ tests/
```

### Type Checking (optional)
```bash
mypy app/
```

## Project Structure

### Application Structure
```
app/
├── __init__.py          # Flask app factory
├── routes/              # URL routes
│   ├── __init__.py
│   ├── main.py         # Main routes
│   ├── api.py          # API endpoints
│   └── health.py       # Health check
├── models/              # Database models
│   ├── __init__.py
│   ├── performer.py    # Performer model
│   ├── studio.py       # Studio model
│   └── scene.py        # Scene model
├── services/            # Business logic
│   ├── __init__.py
│   ├── stash_client.py # Stash API client
│   ├── stashdb_client.py # StashDB client
│   ├── whisparr_client.py # Whisparr client
│   └── scheduler.py    # Job scheduler
└── utils/               # Utilities
    ├── __init__.py
    ├── config.py       # Configuration
    └── helpers.py      # Helper functions
```

### Templates and Static Files
```
templates/               # Jinja2 templates
├── base.html           # Base template
├── index.html          # Dashboard
├── performers.html     # Performers management
└── settings.html       # Settings page

static/                  # Static assets
├── css/
├── js/
└── images/
    └── stash-filter.png # Logo
```

## API Development

### Adding New Endpoints
1. Define route in `app/routes/api.py`
2. Add business logic in appropriate service
3. Update API documentation in `API.md`
4. Add tests in `tests/api/`

### Database Changes
1. Modify models in `app/models/`
2. Create migration script if needed
3. Test with clean database
4. Update documentation

## Debugging

### Enable Debug Mode
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
```

### Database Inspection
```bash
# Connect to SQLite database
sqlite3 data/stash_filter.db
.tables
.schema performers
```

### Log Debugging
- Check `logs/` directory for application logs
- Adjust `LOG_LEVEL` in `.env` for more detail
- Use `docker-compose logs` for container debugging

## Contributing

### Code Standards
- Follow PEP 8 style guide
- Use type hints where possible
- Write docstrings for all functions/classes
- Maintain test coverage above 80%

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run code quality checks
5. Submit pull request

### Commit Messages
Follow conventional commit format:
- `feat:` new features
- `fix:` bug fixes
- `docs:` documentation changes
- `style:` code formatting
- `refactor:` code refactoring
- `test:` adding tests

## Release Process

### Version Bumping
1. Update version in `app/__init__.py`
2. Update `CHANGELOG.md`
3. Create git tag
4. Build and push Docker image

### Docker Release
```bash
# Build multi-arch image
docker buildx build --platform linux/amd64,linux/arm64 -t your-username/stash-filter:latest --push .

# Tag specific version
docker tag your-username/stash-filter:latest your-username/stash-filter:v1.0.0
docker push your-username/stash-filter:v1.0.0
```

## Troubleshooting

### Common Issues
- **Port conflicts**: Change port in docker-compose.yml
- **API connection issues**: Check network connectivity and API keys
- **Database locked**: Ensure only one instance is running
- **Permission errors**: Check file permissions and Docker user

### Getting Help
- Check existing GitHub issues
- Create new issue with full logs
- Join discussions on GitHub Discussions
