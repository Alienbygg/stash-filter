# 🎯 Filtered Scenes Manager - v1.1.0 Feature Implementation Guide

## Overview
This guide will help you implement the **Filtered Scenes Manager** feature in your Stash-Filter project. This feature provides complete visibility and control over scenes that are filtered out during discovery runs.

## 🌟 What This Feature Adds

### **User-Facing Features:**
- **Dashboard with Statistics** - See filtering patterns and exception rates
- **Searchable Scene Library** - Browse all filtered scenes with advanced filters
- **Exception Management** - Create permanent, temporary, or one-time exceptions
- **Bulk Operations** - Handle multiple scenes at once
- **Detailed Scene View** - Complete scene information and filtering reasons
- **Data Management** - Cleanup old data and export functionality

### **Developer Features:**
- **Complete API** - RESTful endpoints for all operations
- **Database Models** - Professional SQLAlchemy models with relationships
- **Migration System** - Safe database schema updates
- **Sample Data Generator** - Testing and demonstration data

## 🛠️ Implementation Steps

### Step 1: Apply Database Migration
```bash
# Navigate to your project directory
cd /mnt/user/appdata/stash-filter/git

# Run the migration to create new tables
python run_migration.py 001_add_filtered_scenes upgrade

# Verify migration was applied
python run_migration.py 001_add_filtered_scenes status
```

### Step 2: Update Your Docker Container
Since you've already pushed the code to GitHub, rebuild your Docker image:

```bash
# Pull latest code (if running from Docker)
docker-compose pull

# Or rebuild if you're building locally
docker-compose build --no-cache

# Restart the container
docker-compose down && docker-compose up -d
```

### Step 3: Generate Test Data (Optional)
```bash
# Generate 100 sample filtered scenes for testing
python generate_sample_data.py --count 100

# Or specify custom database path
python generate_sample_data.py --db-path /path/to/your/database.db --count 50
```

### Step 4: Update Your Scene Discovery Logic
You'll need to integrate the filtered scenes logging into your existing discovery process. Here's an example of how to modify your scene filtering logic:

```python
# Example integration in your scene discovery service
from app.models import FilteredScene, FilterException
from app import db
import json
from datetime import datetime

class SceneDiscoveryService:
    def apply_filters_with_logging(self, scenes):
        """Enhanced filtering with logging for user review."""
        filtered_scenes = []
        passed_scenes = []
        
        for scene in scenes:
            # Check existing filters
            filter_result = self.check_existing_filters(scene)
            
            if filter_result['filtered']:
                # Check for active exceptions first
                if not self.has_active_exception(scene):
                    # Log filtered scene to database
                    self.log_filtered_scene(scene, filter_result)
                    filtered_scenes.append(scene)
                else:
                    # Scene has exception, allow it through
                    passed_scenes.append(scene)
                    self.log_exception_used(scene)
            else:
                passed_scenes.append(scene)
        
        return passed_scenes

    def log_filtered_scene(self, scene, filter_result):
        """Log filtered scene for user review."""
        try:
            # Extract scene information
            performers = [p.get('name') for p in scene.get('performers', [])]
            studio = scene.get('studio', {}).get('name') if scene.get('studio') else None
            tags = [t.get('name') for t in scene.get('tags', [])]
            
            # Create filtered scene record
            filtered_scene = FilteredScene(
                stash_id=scene.get('id'),
                stashdb_id=scene.get('stash_ids', [{}])[0].get('stash_id') if scene.get('stash_ids') else None,
                title=scene.get('title', 'Unknown Title'),
                performers=json.dumps(performers),
                studio=studio,
                tags=json.dumps(tags),
                duration=scene.get('file', {}).get('duration') if scene.get('file') else None,
                release_date=scene.get('date'),
                filter_reason=filter_result['reason'],
                filter_category=filter_result['category'],
                filter_details=json.dumps(filter_result.get('details', {})),
                scene_url=scene.get('url'),
                thumbnail_url=scene.get('image'),
                filtered_date=datetime.utcnow()
            )
            
            db.session.add(filtered_scene)
            db.session.commit()
            
        except Exception as e:
            print(f"Error logging filtered scene: {e}")
            db.session.rollback()

    def has_active_exception(self, scene):
        """Check if scene has an active exception."""
        try:
            # Look for scene by Stash ID or title
            scene_id = scene.get('id')
            scene_title = scene.get('title')
            
            # Query for existing filtered scene with active exception
            filtered_scene = FilteredScene.query.filter(
                db.or_(
                    FilteredScene.stash_id == scene_id,
                    FilteredScene.title == scene_title
                )
            ).first()
            
            if filtered_scene and filtered_scene.has_active_exception:
                return True
                
            return False
            
        except Exception as e:
            print(f"Error checking exceptions: {e}")
            return False
    
    def log_exception_used(self, scene):
        """Log when an exception is used to allow a scene through."""
        try:
            # Find the exception and mark it as used
            filtered_scene = FilteredScene.query.filter(
                db.or_(
                    FilteredScene.stash_id == scene.get('id'),
                    FilteredScene.title == scene.get('title')
                )
            ).first()
            
            if filtered_scene:
                for exception in filtered_scene.exceptions:
                    if exception.is_valid:
                        exception.use_exception()
                        db.session.commit()
                        break
                        
        except Exception as e:
            print(f"Error logging exception usage: {e}")
            db.session.rollback()
```

## 🎛️ Using the Feature

### Accessing the Interface
1. Start your Stash-Filter application
2. Navigate to **"Filtered Scenes"** in the main navigation
3. The dashboard will show statistics and allow you to browse filtered scenes

### Dashboard Overview
- **Total Filtered** - Number of scenes filtered in the last 30 days
- **Exceptions** - Number of active exception overrides
- **Exception Rate** - Percentage of filtered scenes that were rescued
- **Top Filter** - Most common reason scenes are filtered

### Creating Exceptions
1. **Individual Exceptions:**
   - Click the green checkmark button next to any filtered scene
   - Choose exception type (permanent, temporary, one-time)
   - Optionally add to Whisparr for immediate download

2. **Bulk Exceptions:**
   - Select multiple scenes using checkboxes
   - Click "Create Exceptions" in the bulk actions bar
   - Apply the same exception type to all selected scenes

### Exception Types
- **Permanent** - Scene will never be filtered again
- **Temporary** - Scene allowed until specified expiration date
- **One-time** - Scene allowed for the next discovery run only

### Search and Filtering
- **Filter Reason** - View scenes filtered for specific reasons
- **Exception Status** - Show only scenes with/without exceptions
- **Date Range** - Filter by when scenes were filtered
- **Search** - Search in titles, performers, and studios

### Data Management
- **Cleanup** - Remove old filtered scenes (configurable retention period)
- **Export** - Download filtered scenes data as CSV
- **Auto-refresh** - Statistics update every 5 minutes

## 🔧 Configuration Options

### Environment Variables
Add these to your `.env` file for additional configuration:

```env
# Filtered scenes retention (days)
FILTERED_SCENES_RETENTION_DAYS=90

# Auto-cleanup schedule (cron format)
FILTERED_SCENES_CLEANUP_SCHEDULE="0 2 * * 0"  # Weekly at 2 AM

# Maximum scenes to display per page
FILTERED_SCENES_PER_PAGE=20

# Enable exception notifications
FILTERED_SCENES_NOTIFY_EXCEPTIONS=true
```

## 📊 API Endpoints

### Core Endpoints
- `GET /api/filtered-scenes` - List filtered scenes with pagination and filters
- `GET /api/filtered-scenes/stats` - Get filtering statistics  
- `GET /api/filtered-scenes/{id}` - Get specific filtered scene details
- `POST /api/filtered-scenes/{id}/exception` - Create exception for scene
- `POST /api/filtered-scenes/bulk-exception` - Create bulk exceptions
- `PUT /api/exceptions/{id}` - Update existing exception
- `DELETE /api/exceptions/{id}` - Delete exception
- `POST /api/filtered-scenes/cleanup` - Clean up old data

### Example API Usage
```bash
# Get filtering statistics
curl -X GET http://localhost:5000/api/filtered-scenes/stats

# Create permanent exception for scene
curl -X POST http://localhost:5000/api/filtered-scenes/123/exception \
  -H "Content-Type: application/json" \
  -d '{"type": "permanent", "reason": "User requested", "add_to_whisparr": true}'

# Get filtered scenes with filters
curl -X GET "http://localhost:5000/api/filtered-scenes?filter_reason=unwanted_tags&has_exception=false&page=1"
```

## 🧪 Testing the Feature

### Manual Testing Checklist
- [ ] Dashboard loads and shows statistics
- [ ] Scene table displays with proper pagination
- [ ] Search and filters work correctly
- [ ] Exception creation modal functions
- [ ] Bulk operations work with multiple selections
- [ ] Scene details modal shows complete information
- [ ] Data cleanup removes old records
- [ ] Export functionality downloads CSV

### Automated Testing
```bash
# Run the test suite (if you have tests)
python -m pytest tests/ -v

# Test API endpoints
python -m pytest tests/test_filtered_scenes_api.py -v
```

## 🔄 Integration with Existing Code

### Scheduler Integration
Add to your discovery scheduler to log filtered scenes:

```python
# In your scheduled discovery job
def run_discovery():
    discovery_service = SceneDiscoveryService()
    
    # Your existing discovery logic
    all_scenes = discovery_service.discover_new_scenes()
    
    # Enhanced filtering with logging
    passed_scenes = discovery_service.apply_filters_with_logging(all_scenes)
    
    # Process passed scenes as before
    wanted_scenes = discovery_service.add_to_wanted_list(passed_scenes)
    
    return {
        'discovered': len(all_scenes),
        'filtered': len(all_scenes) - len(passed_scenes),
        'wanted': len(wanted_scenes)
    }
```

### Webhook Integration
Notify when exceptions are created:

```python
# Optional webhook for exception notifications
def notify_exception_created(exception):
    if os.environ.get('FILTERED_SCENES_NOTIFY_EXCEPTIONS') == 'true':
        webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
        if webhook_url:
            scene = exception.filtered_scene
            message = f"Exception created for '{scene.title}' - {exception.exception_type}"
            # Send webhook notification
```

## 🚀 Version 1.1.0 Release Notes

### New Features
- **Filtered Scenes Manager** - Complete visibility into filtered content
- **Exception System** - Override filters with permanent, temporary, or one-time exceptions
- **Statistics Dashboard** - Monitor filtering patterns and trends
- **Bulk Operations** - Manage multiple scenes efficiently
- **Data Management** - Cleanup and export tools

### Database Changes
- Added `filtered_scenes` table for tracking filtered content
- Added `filter_exceptions` table for managing overrides
- Added migration system for safe schema updates

### API Additions
- 8+ new REST API endpoints for filtered scenes management
- Comprehensive filtering and search capabilities
- Bulk operation support

## 🎉 You're Ready to Launch v1.1.0!

Your **Filtered Scenes Manager** feature is now complete and ready for users! This addition will make Stash-Filter much more transparent and user-friendly while maintaining its automated efficiency.

The community will love having visibility into what's being filtered and the ability to rescue scenes they actually want. This addresses one of the biggest requests from automation tool users - **transparency and control**.

**Next Steps:**
1. Apply the database migration
2. Test the functionality with sample data
3. Create your v1.1.0 release on GitHub
4. Update your documentation
5. Announce the new feature to the community!

This is a **major feature** that significantly enhances the user experience. Great work on building something the community genuinely needs! 🌟
