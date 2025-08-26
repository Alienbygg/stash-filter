# Stash-Filter - Unraid Community Applications Submission

## Application Information

**Name:** Stash-Filter  
**Author:** Alienbygg  
**Category:** MediaApp:Video, MediaServer:Video, Tools:Utilities  
**Repository:** alienbygg/stash-filter  
**Docker Hub:** https://hub.docker.com/r/alienbygg/stash-filter  
**GitHub:** https://github.com/Alienbygg/stash-filter  
**Support:** https://github.com/Alienbygg/stash-filter/issues  

## Description

Stash-Filter is a professional Docker application that automatically discovers new scenes for your favorite performers and studios. It integrates seamlessly with Stash, StashDB, and Whisparr to provide comprehensive content discovery and management.

### Key Features

**🎯 NEW in v1.1.0: Filtered Scenes Manager**
- Complete visibility into what gets filtered and why
- Create exceptions to rescue wanted scenes (permanent/temporary/one-time)
- Analytics dashboard showing filtering patterns and trends
- Bulk operations for efficient scene management

**🔍 Core Functionality:**
- Daily automated content discovery from StashDB
- Smart filtering system (duplicates, unwanted tags, studios, duration)
- Professional web interface with responsive design
- Complete Whisparr integration for automatic downloads
- Local SQLite database with health monitoring
- Comprehensive logging and error handling

**🛠️ Perfect For:**
- Stash users wanting automated content discovery
- Self-hosted media enthusiasts managing large libraries
- Users who want transparency and control over automation

## Technical Details

- **Base Image:** Python 3.11-slim
- **Architecture:** Multi-arch (AMD64, ARM64)
- **Database:** SQLite (local storage)
- **Web Framework:** Flask with responsive Bootstrap UI
- **Health Checks:** Built-in health monitoring
- **Security:** Runs as non-root user, no privileged access required

## Requirements

- **Stash Server:** Running and accessible on local network with API enabled
- **Optional:** Whisparr for automatic scene downloads
- **Optional:** StashDB API key for enhanced discovery features

## Default Ports

- **WebUI:** 5000 (configurable)

## Volume Mounts

- `/app/data` - Application database and configuration
- `/app/logs` - Application logs and monitoring
- `/app/config` - Additional configuration files

## Environment Variables

**Required:**
- `STASH_URL` - Your Stash server URL (e.g., http://192.168.1.100:9999)
- `STASH_API_KEY` - Stash API key from Settings > Security

**Optional:**
- `WHISPARR_URL` - Whisparr server URL for downloads
- `WHISPARR_API_KEY` - Whisparr API key
- `STASHDB_API_KEY` - StashDB API key for enhanced features
- `LOG_LEVEL` - Logging level (INFO, DEBUG, WARNING, ERROR)

## Installation Notes

1. **First Time Setup:**
   - Install and configure Stash with API access enabled
   - Configure your favorite performers and studios in Stash
   - Install Stash-Filter using this template
   - Access the web interface to sync favorites and configure filters

2. **Migration from v1.0.x:**
   - Database migration runs automatically on first start
   - No manual intervention required
   - Existing configurations are preserved

## Support & Documentation

- **GitHub Issues:** https://github.com/Alienbygg/stash-filter/issues
- **Documentation:** Complete guides in repository
- **API Reference:** Full REST API documentation included
- **Community:** Active development with regular updates

## Screenshots

The application includes:
- Professional dashboard with statistics and recent activity
- Comprehensive scene management with advanced filtering
- Settings page for complete configuration control
- Filtered scenes manager with exception handling
- Health monitoring and logging interface

## Changelog

**v1.1.0 (Latest):**
- NEW: Complete Filtered Scenes Manager with analytics
- NEW: Exception system for overriding filters
- NEW: Bulk operations and data management tools
- Enhanced: Professional web interface
- Enhanced: 8+ new API endpoints
- Enhanced: Database migration system

**v1.0.0:**
- Initial public release
- Core discovery and filtering functionality
- Stash, StashDB, and Whisparr integration
- Professional Docker deployment

---

## Community Applications Submission Checklist

- [x] Template follows Unraid XML schema
- [x] Docker image published to Docker Hub
- [x] Multi-architecture support (AMD64/ARM64)
- [x] Comprehensive documentation
- [x] Support forum established (GitHub Issues)
- [x] Professional icon and branding
- [x] Health checks implemented
- [x] Non-root user execution
- [x] Proper volume mounts and permissions
- [x] Environment variable configuration
- [x] Clear installation instructions
- [x] Active maintenance and updates

This application has been thoroughly tested and is production-ready for the Unraid community.
