# Stash-Filter API Documentation

## Overview
This document describes the REST API endpoints available in Stash-Filter.

## Base URL
```
http://localhost:5000
```

## Authentication
Currently, no authentication is required for API access as the application is designed for local network use.

## Content Type
All API endpoints accept and return JSON data unless otherwise specified.

```
Content-Type: application/json
```

## API Endpoints

### Health Check

#### GET /health
Check if the application is running and healthy.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-20T10:30:00.000Z"
}
```

### Favorites Management

#### POST /api/sync-favorites
Synchronize favorite performers and studios from Stash.

**Request Body:** None

**Response:**
```json
{
  "status": "success",
  "message": "Favorites synced successfully"
}
```

**Error Response:**
```json
{
  "status": "error",
  "message": "Error message details"
}
```

### Monitoring Management

#### POST /api/toggle-monitoring
Toggle monitoring status for a performer or studio.

**Request Body:**
```json
{
  "type": "performer",  // or "studio"
  "id": 123
}
```

**Response:**
```json
{
  "status": "success",
  "monitored": true
}
```

### Discovery

#### POST /api/run-discovery
Manually trigger the scene discovery process.

**Request Body:** None

**Response:**
```json
{
  "status": "success",
  "new_scenes": 15,
  "filtered_scenes": 3,
  "wanted_added": 12,
  "errors": []
}
```

### Settings Management

#### POST /api/save-settings
Save application configuration settings.

**Request Body:**
```json
{
  "discovery_enabled": true,
  "discovery_frequency_hours": 24,
  "max_scenes_per_check": 100,
  "unwanted_categories": ["anal", "bdsm"],
  "required_categories": ["lesbian"],
  "min_duration_minutes": 10,
  "max_duration_minutes": 180,
  "auto_add_to_whisparr": true,
  "whisparr_quality_profile": "HD"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Settings saved successfully"
}
```

#### POST /api/test-connections
Test connections to external APIs.

**Request Body:** None

**Response:**
```json
{
  "stash": true,
  "stashdb": true,
  "whisparr": false
}
```

### Wanted Scenes Management

#### POST /api/add-to-whisparr
Add a specific wanted scene to Whisparr.

**Request Body:**
```json
{
  "wanted_id": 123
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Scene added to Whisparr successfully"
}
```

#### POST /api/add-all-to-whisparr
Add multiple wanted scenes to Whisparr.

**Request Body:**
```json
{
  "wanted_ids": [123, 124, 125]
}
```

**Response:**
```json
{
  "status": "success",
  "added_count": 3,
  "message": "3 scenes added to Whisparr successfully"
}
```

#### DELETE /api/remove-wanted
Remove a scene from the wanted list.

**Request Body:**
```json
{
  "wanted_id": 123
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Scene removed from wanted list"
}
```

#### POST /api/refresh-whisparr-status
Refresh the download status of scenes in Whisparr.

**Request Body:** None

**Response:**
```json
{
  "status": "success",
  "updated_count": 5,
  "message": "Status refreshed for 5 scenes"
}
```

## Data Models

### Performer
```json
{
  "id": 1,
  "stash_id": "123",
  "stashdb_id": "abc-def-ghi",
  "name": "Performer Name",
  "aliases": ["Alias1", "Alias2"],
  "monitored": true,
  "last_checked": "2025-01-20T10:30:00.000Z",
  "created_date": "2025-01-15T08:00:00.000Z"
}
```

### Studio
```json
{
  "id": 1,
  "stash_id": "456",
  "stashdb_id": "xyz-uvw-rst",
  "name": "Studio Name",
  "parent_studio": "Parent Studio Name",
  "monitored": true,
  "last_checked": "2025-01-20T10:30:00.000Z",
  "created_date": "2025-01-15T08:00:00.000Z"
}
```

### Scene
```json
{
  "id": 1,
  "stashdb_id": "scene-abc-123",
  "title": "Scene Title",
  "release_date": "2025-01-15",
  "duration": 1800,
  "tags": ["tag1", "tag2"],
  "categories": ["category1", "category2"],
  "performer_id": 1,
  "studio_id": 1,
  "is_owned": false,
  "is_wanted": true,
  "is_filtered": false,
  "filter_reason": null,
  "discovered_date": "2025-01-20T10:30:00.000Z"
}
```

### WantedScene
```json
{
  "id": 1,
  "scene_id": 1,
  "whisparr_id": "whisparr-123",
  "title": "Scene Title",
  "performer_name": "Performer Name",
  "studio_name": "Studio Name",
  "release_date": "2025-01-15",
  "status": "wanted",
  "added_to_whisparr": false,
  "download_status": null,
  "added_date": "2025-01-20T10:30:00.000Z"
}
```

### Config
```json
{
  "id": 1,
  "unwanted_categories": ["anal", "bdsm"],
  "required_categories": ["lesbian"],
  "discovery_enabled": true,
  "discovery_frequency_hours": 24,
  "max_scenes_per_check": 100,
  "min_duration_minutes": 10,
  "max_duration_minutes": 180,
  "auto_add_to_whisparr": true,
  "whisparr_quality_profile": "HD"
}
```

## Error Handling

### Error Response Format
```json
{
  "status": "error",
  "message": "Error description",
  "code": "ERROR_CODE",
  "details": {}
}
```

### HTTP Status Codes
- `200 OK` - Successful request
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

### Common Error Codes
- `INVALID_REQUEST` - Request format is invalid
- `MISSING_PARAMETER` - Required parameter is missing
- `RESOURCE_NOT_FOUND` - Requested resource doesn't exist
- `API_CONNECTION_ERROR` - External API connection failed
- `DATABASE_ERROR` - Database operation failed
- `CONFIGURATION_ERROR` - Configuration is invalid

## Rate Limiting
Currently, no rate limiting is implemented. This may be added in future versions.

## Webhooks
Webhook support is planned for future releases to notify external systems of events.

## External API Integration

### Stash API
The application integrates with Stash's GraphQL API to:
- Retrieve favorite performers and studios
- Check if scenes already exist
- Get scene metadata

### StashDB API
Integration with StashDB's GraphQL API to:
- Search for performers and studios
- Retrieve scene information
- Get scene metadata and tags

### Whisparr API
Integration with Whisparr's REST API to:
- Add movies/scenes for download
- Check download status
- Manage quality profiles

## Usage Examples

### Sync Favorites
```bash
curl -X POST http://localhost:5000/api/sync-favorites \
  -H "Content-Type: application/json"
```

### Run Discovery
```bash
curl -X POST http://localhost:5000/api/run-discovery \
  -H "Content-Type: application/json"
```

### Toggle Monitoring
```bash
curl -X POST http://localhost:5000/api/toggle-monitoring \
  -H "Content-Type: application/json" \
  -d '{"type": "performer", "id": 123}'
```

### Save Settings
```bash
curl -X POST http://localhost:5000/api/save-settings \
  -H "Content-Type: application/json" \
  -d '{
    "discovery_enabled": true,
    "unwanted_categories": ["anal", "bdsm"],
    "auto_add_to_whisparr": true
  }'
```

### Add Scene to Whisparr
```bash
curl -X POST http://localhost:5000/api/add-to-whisparr \
  -H "Content-Type: application/json" \
  -d '{"wanted_id": 123}'
```

## SDK and Client Libraries
Currently, no official SDK is available. Developers can use standard HTTP clients to interact with the API.

## Changelog

### Version 1.0.0
- Initial API implementation
- Core endpoints for discovery and management
- Integration with Stash, StashDB, and Whisparr

### Future Versions
- Authentication and authorization
- Webhook support
- Enhanced filtering options
- Bulk operations
- API versioning
