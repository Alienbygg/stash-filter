# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2025-08-26

### 🎯 Major Feature: Filtered Scenes Manager

A comprehensive management system for viewing, analyzing, and creating exceptions for filtered scenes. This addresses one of the most requested features - **transparency and control over automated filtering**.

#### Added
- **Filtered Scenes Dashboard** - Statistics and analytics for filtering patterns
  - Total filtered scenes count (configurable time periods)
  - Exception rate tracking and trends
  - Filter reason breakdown with visual charts
  - Most common filter categories analysis
  - Recent activity timeline (7-day view)
  - Top filtered studios identification

- **Advanced Scene Browser** - Comprehensive filtered scene management
  - Paginated table view with thumbnail previews
  - Advanced search across titles, performers, and studios
  - Multi-criteria filtering (reason, category, date range, exception status)
  - Sortable columns with responsive design
  - Bulk selection and operations
  - Real-time search with debounced input

- **Exception Management System** - Override filters with granular control
  - **Permanent Exceptions** - Never filter these scenes again
  - **Temporary Exceptions** - Allow scenes until specific expiration date
  - **One-time Exceptions** - Allow for next discovery run only
  - Bulk exception creation for multiple scenes
  - Exception usage tracking and statistics
  - Automatic expiration handling
  - Integration with Whisparr for immediate downloads

- **Scene Detail View** - Complete scene information and filtering context
  - Full scene metadata (performers, studio, tags, duration)
  - Detailed filter reasoning and criteria
  - Exception history and status
  - Direct links to source content
  - Thumbnail preview with fallback placeholders

- **Data Management Tools** - Maintenance and export functionality
  - Configurable data cleanup (retention periods)
  - CSV export with current filters applied
  - Bulk operations for maintenance
  - Database optimization tools

#### Database Schema
- **New Table: `filtered_scenes`** - Track all filtered content
  - Scene metadata (title, performers, studio, tags)
  - Filtering information (reason, category, details)
  - Exception status and history
  - Timestamps and source URLs
  - Performance-optimized indexes

- **New Table: `filter_exceptions`** - Manage filtering overrides
  - Exception types and configurations
  - Expiration handling for temporary exceptions
  - Usage tracking and statistics
  - Relationship management with filtered scenes
  - Auto-cleanup for expired exceptions

- **Migration System** - Safe schema updates
  - Version-controlled database migrations
  - Rollback capability for safety
  - Migration status tracking
  - Automated migration runner

#### API Enhancements
- **8 New REST Endpoints** for filtered scenes management
  - `GET /api/filtered-scenes` - Paginated scene listing with filters
  - `GET /api/filtered-scenes/stats` - Comprehensive statistics
  - `GET /api/filtered-scenes/{id}` - Individual scene details
  - `POST /api/filtered-scenes/{id}/exception` - Create scene exception
  - `POST /api/filtered-scenes/bulk-exception` - Bulk exception creation
  - `PUT /api/exceptions/{id}` - Update existing exceptions
  - `DELETE /api/exceptions/{id}` - Remove exceptions
  - `POST /api/filtered-scenes/cleanup` - Data cleanup operations

- **Enhanced Discovery Integration** - Automatic filtered scene logging
  - Scene filtering with comprehensive logging
  - Exception checking during discovery
  - Usage statistics for exceptions
  - Performance-optimized database queries

#### Frontend Features
- **Responsive React-like Interface** - Modern, mobile-friendly design
  - Bootstrap 5 with custom styling
  - Font Awesome icons throughout
  - Loading states and error handling
  - Toast notifications for user feedback
  - Modal dialogs for detailed operations

- **Advanced JavaScript Functionality** - Rich client-side features
  - Real-time search with 500ms debouncing
  - Dynamic pagination with page size options
  - Bulk selection with "select all" functionality
  - Form validation with user-friendly error messages
  - Auto-refresh for statistics (5-minute intervals)

#### Developer Tools
- **Sample Data Generator** - Testing and demonstration
  - Generate realistic filtered scene data
  - Configurable data volumes (10-1000+ scenes)
  - Multiple filter reasons and categories
  - Realistic exception scenarios
  - Easy cleanup for development

- **Migration Runner** - Database management
  - Command-line migration tool
  - Status checking and validation
  - Safe upgrade/downgrade operations
  - Development environment support

#### User Experience Improvements
- **Navigation Enhancement** - Updated main navigation
  - New "Filtered Scenes" menu item
  - Badge counters for filtered scene counts
  - Improved navigation flow
  - Consistent icon usage throughout

- **Performance Optimizations** - Faster page loads and interactions
  - Database query optimization with proper indexing
  - Paginated data loading (default 20 items per page)
  - Efficient bulk operations
  - Reduced memory usage with lazy loading

### Technical Implementation
- **Backend Architecture** - Professional Python implementation
  - SQLAlchemy models with proper relationships
  - Comprehensive error handling and logging
  - Input validation and sanitization
  - RESTful API design patterns
  - Database transaction management

- **Frontend Architecture** - Modern JavaScript practices
  - ES6+ features with browser compatibility
  - Modular code organization
  - Event-driven architecture
  - Efficient DOM manipulation
  - Bootstrap 5 component integration

- **Database Design** - Optimized for performance
  - Proper foreign key relationships
  - Strategic indexes for common queries
  - JSON field usage for flexible data
  - Automatic timestamp management
  - Cascade deletion for data integrity

### Configuration Options
- **New Environment Variables** - Enhanced customization
  ```env
  FILTERED_SCENES_RETENTION_DAYS=90
  FILTERED_SCENES_PER_PAGE=20
  FILTERED_SCENES_AUTO_CLEANUP=true
  FILTERED_SCENES_NOTIFY_EXCEPTIONS=false
  ```

### Documentation
- **Implementation Guide** - Complete setup documentation
  - Step-by-step implementation instructions
  - Integration examples with existing code
  - API usage examples with curl commands
  - Testing procedures and checklists
  - Migration and upgrade procedures

### Breaking Changes
- **Database Schema** - New tables require migration
  - Run `python run_migration.py 001_add_filtered_scenes upgrade`
  - Backup your database before migration
  - Migration is reversible with downgrade option

### Upgrade Instructions
1. **Backup Database** - Always backup before major updates
2. **Pull Latest Code** - Update from GitHub repository
3. **Run Migration** - Apply database schema changes
4. **Restart Services** - Restart Docker containers
5. **Verify Functionality** - Test new features

### Future Enhancements (Planned for v1.2.0)
- Advanced filtering rules editor
- Custom filter reason categories
- Exception templates for common scenarios
- Webhook notifications for exceptions
- Detailed analytics and reporting
- Integration with external notification services

---

*This release represents a major step forward in user control and transparency. The Filtered Scenes Manager provides complete visibility into the filtering process while maintaining the automated efficiency that makes Stash-Filter valuable.*

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
