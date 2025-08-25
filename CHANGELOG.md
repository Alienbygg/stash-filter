# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-01-20

### Added
- Initial release of Stash-Filter Docker application
- Web-based dashboard for managing favorite performers and studios
- Daily automated scene discovery from StashDB
- Smart filtering system to exclude unwanted content
- Integration with Stash for checking existing scenes
- Integration with Whisparr for automatic downloads
- SQLite database for tracking discovered scenes and preferences
- RESTful API for all major operations
- Docker containerization with health checks
- Unraid Docker template for easy deployment
- Comprehensive logging and error handling
- Settings management interface
- Manual discovery trigger
- Bulk operations for wanted scenes

### Core Features
- **Content Discovery**: Daily checks for new scenes from favorite performers/studios
- **Smart Filtering**: Filter out scenes by categories, duration, and existing content
- **Database Tracking**: Local SQLite database for persistent data
- **Web Interface**: Responsive web UI for all management tasks
- **API Integration**: Full integration with Stash, StashDB, and Whisparr APIs
- **Health Monitoring**: Built-in health checks and status monitoring

### API Endpoints
- `/health` - Application health check
- `/api/sync-favorites` - Sync favorites from Stash
- `/api/toggle-monitoring` - Enable/disable monitoring for performers/studios
- `/api/run-discovery` - Manual scene discovery trigger
- `/api/save-settings` - Configuration management
- `/api/test-connections` - Test external API connections
- `/api/add-to-whisparr` - Add scenes to Whisparr
- `/api/remove-wanted` - Remove scenes from wanted list
- `/api/refresh-whisparr-status` - Update download status

### Technical Details
- Python 3.11 with Flask web framework
- SQLite database with SQLAlchemy ORM
- Docker containerization with multi-stage builds
- Cron-based scheduling for automated tasks
- GraphQL integration with Stash and StashDB
- REST API integration with Whisparr
- Comprehensive error handling and logging
- Health check endpoints for monitoring

### Documentation
- Complete README with setup instructions
- API documentation with examples
- Development guide for contributors
- Unraid template for easy deployment
- Contributing guidelines
- MIT License

### Configuration Options
- Customizable unwanted categories filtering
- Required categories enforcement
- Duration-based filtering (min/max minutes)
- Discovery frequency configuration
- Maximum scenes per check limit
- Automatic Whisparr integration toggle
- Quality profile selection for Whisparr

### Security Features
- Environment variable configuration for sensitive data
- API key masking in Unraid template
- No hardcoded credentials or personal information
- Local network operation (no external authentication required)

## [0.9.0] - 2025-01-15

### Added
- Beta testing version
- Core functionality implementation
- Initial Docker containerization
- Basic web interface

### Changed
- Improved error handling
- Enhanced logging system
- Optimized database queries

### Fixed
- Connection timeout issues with external APIs
- Memory leak in scene processing
- UI responsiveness on mobile devices

---

## Version History Legend

- **Added** for new features
- **Changed** for changes in existing functionality  
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes

## Migration Notes

### From 0.x to 1.0.0
- Database will be automatically upgraded on first run
- Environment variables have changed - see `.env.example`
- Docker image repository may change - update your compose files
- Some API endpoints have been renamed for consistency

## Support

For questions about specific versions or upgrade issues:
- Check the [README.md](README.md) for current setup instructions
- Review [DEVELOPMENT.md](DEVELOPMENT.md) for development changes
- Open an issue on GitHub for version-specific problems
- Check the [API documentation](API.md) for endpoint changes

## Future Releases

### Planned for 1.1.0
- [ ] Enhanced filtering with custom rules
- [ ] Webhook notifications
- [ ] Performance analytics dashboard
- [ ] Multi-language support
- [ ] Advanced scheduling options

### Planned for 1.2.0
- [ ] User authentication system
- [ ] Multi-tenant support
- [ ] Enhanced API with pagination
- [ ] Scene recommendation engine
- [ ] Advanced reporting features

### Planned for 2.0.0
- [ ] Complete UI redesign
- [ ] Plugin architecture
- [ ] Cloud deployment options
- [ ] Advanced machine learning features
- [ ] Mobile app companion
