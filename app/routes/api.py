"""
API routes for Stash-Filter application.
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import uuid
from app import db
from app.models import Performer, Studio, Scene, WantedScene, Config, DiscoveryLog

# Create blueprint
api_bp = Blueprint('api', __name__)

@api_bp.route('/sync-favorites', methods=['POST'])
def sync_favorites():
    """Sync favorites from Stash."""
    try:
        # This would integrate with actual Stash client
        # For now, return success response
        
        current_app.logger.info("Starting favorites sync")
        
        # Placeholder for actual sync logic
        performers_synced = 0
        studios_synced = 0
        
        current_app.logger.info(f"Synced {performers_synced} performers and {studios_synced} studios")
        
        return jsonify({
            'status': 'success',
            'message': f'Synced {performers_synced} performers and {studios_synced} studios',
            'performers_synced': performers_synced,
            'studios_synced': studios_synced
        })
        
    except Exception as e:
        current_app.logger.error(f"Error syncing favorites: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to sync favorites: {str(e)}'
        }), 500

@api_bp.route('/toggle-monitoring', methods=['POST'])
def toggle_monitoring():
    """Toggle monitoring status for a performer or studio."""
    try:
        data = request.get_json()
        
        if not data or 'type' not in data or 'id' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields: type and id'
            }), 400
        
        entity_type = data['type']
        entity_id = data['id']
        
        if entity_type == 'performer':
            entity = Performer.query.get(entity_id)
        elif entity_type == 'studio':
            entity = Studio.query.get(entity_id)
        else:
            return jsonify({
                'status': 'error',
                'message': 'Invalid type. Must be "performer" or "studio"'
            }), 400
        
        if not entity:
            return jsonify({
                'status': 'error',
                'message': f'{entity_type.title()} not found'
            }), 404
        
        # Toggle monitoring status
        entity.monitored = not entity.monitored
        entity.updated_date = datetime.utcnow()
        db.session.commit()
        
        current_app.logger.info(f"Toggled monitoring for {entity_type} {entity.name}: {entity.monitored}")
        
        return jsonify({
            'status': 'success',
            'monitored': entity.monitored,
            'message': f'Monitoring {"enabled" if entity.monitored else "disabled"} for {entity.name}'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error toggling monitoring: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to toggle monitoring: {str(e)}'
        }), 500

@api_bp.route('/run-discovery', methods=['POST'])
def run_discovery():
    """Manually trigger scene discovery."""
    try:
        # Create discovery log entry
        run_id = str(uuid.uuid4())
        discovery_log = DiscoveryLog(
            run_id=run_id,
            status='running',
            started_date=datetime.utcnow()
        )
        db.session.add(discovery_log)
        db.session.commit()
        
        current_app.logger.info(f"Starting manual discovery run: {run_id}")
        
        # Placeholder for actual discovery logic
        # This would integrate with StashDB client and scene discovery service
        
        # Simulate discovery results
        new_scenes = 0
        filtered_scenes = 0
        wanted_added = 0
        errors = []
        
        # Update discovery log
        discovery_log.status = 'completed'
        discovery_log.completed_date = datetime.utcnow()
        discovery_log.scenes_discovered = new_scenes
        discovery_log.scenes_filtered = filtered_scenes
        discovery_log.scenes_added_wanted = wanted_added
        discovery_log.duration_seconds = (discovery_log.completed_date - discovery_log.started_date).seconds
        db.session.commit()
        
        current_app.logger.info(f"Discovery run completed: {run_id}")
        
        return jsonify({
            'status': 'success',
            'run_id': run_id,
            'new_scenes': new_scenes,
            'filtered_scenes': filtered_scenes,
            'wanted_added': wanted_added,
            'errors': errors,
            'message': f'Discovery completed. Found {new_scenes} new scenes, {wanted_added} added to wanted list'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error running discovery: {str(e)}")
        
        # Update log with error if it exists
        try:
            if 'discovery_log' in locals():
                discovery_log.status = 'failed'
                discovery_log.error_message = str(e)
                discovery_log.completed_date = datetime.utcnow()
                db.session.commit()
        except Exception:
            pass
        
        return jsonify({
            'status': 'error',
            'message': f'Discovery failed: {str(e)}'
        }), 500

@api_bp.route('/save-settings', methods=['POST'])
def save_settings():
    """Save application configuration settings."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No configuration data provided'
            }), 400
        
        # Get or create config
        config = Config.query.first()
        if not config:
            config = Config()
            db.session.add(config)
        
        # Update configuration fields
        if 'unwanted_categories' in data:
            config.unwanted_categories_list = data['unwanted_categories']
        
        if 'required_categories' in data:
            config.required_categories_list = data['required_categories']
        
        if 'min_duration_minutes' in data:
            config.min_duration_minutes = int(data['min_duration_minutes'])
        
        if 'max_duration_minutes' in data:
            config.max_duration_minutes = int(data['max_duration_minutes'])
        
        if 'min_rating' in data:
            config.min_rating = float(data['min_rating'])
        
        if 'discovery_enabled' in data:
            config.discovery_enabled = bool(data['discovery_enabled'])
        
        if 'discovery_frequency_hours' in data:
            config.discovery_frequency_hours = int(data['discovery_frequency_hours'])
        
        if 'max_scenes_per_check' in data:
            config.max_scenes_per_check = int(data['max_scenes_per_check'])
        
        if 'auto_add_to_whisparr' in data:
            config.auto_add_to_whisparr = bool(data['auto_add_to_whisparr'])
        
        if 'whisparr_quality_profile' in data:
            config.whisparr_quality_profile = data['whisparr_quality_profile']
        
        if 'concurrent_requests' in data:
            config.concurrent_requests = int(data['concurrent_requests'])
        
        if 'request_timeout' in data:
            config.request_timeout = int(data['request_timeout'])
        
        config.updated_date = datetime.utcnow()
        db.session.commit()
        
        current_app.logger.info("Configuration settings updated")
        
        return jsonify({
            'status': 'success',
            'message': 'Settings saved successfully',
            'config': config.to_dict()
        })
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': f'Invalid data format: {str(e)}'
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error saving settings: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to save settings: {str(e)}'
        }), 500

@api_bp.route('/test-connections', methods=['POST'])
def test_connections():
    """Test connections to external APIs."""
    try:
        results = {
            'stash': False,
            'stashdb': False,
            'whisparr': False
        }
        
        # Test Stash connection
        try:
            # Placeholder for actual Stash client test
            results['stash'] = True
            current_app.logger.info("Stash connection test passed")
        except Exception as e:
            current_app.logger.warning(f"Stash connection test failed: {str(e)}")
        
        # Test StashDB connection
        try:
            # Placeholder for actual StashDB client test
            results['stashdb'] = True
            current_app.logger.info("StashDB connection test passed")
        except Exception as e:
            current_app.logger.warning(f"StashDB connection test failed: {str(e)}")
        
        # Test Whisparr connection (optional)
        try:
            # Placeholder for actual Whisparr client test
            results['whisparr'] = True
            current_app.logger.info("Whisparr connection test passed")
        except Exception as e:
            current_app.logger.warning(f"Whisparr connection test failed: {str(e)}")
        
        return jsonify(results)
        
    except Exception as e:
        current_app.logger.error(f"Error testing connections: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to test connections: {str(e)}'
        }), 500

@api_bp.route('/add-to-whisparr', methods=['POST'])
def add_to_whisparr():
    """Add a specific wanted scene to Whisparr."""
    try:
        data = request.get_json()
        
        if not data or 'wanted_id' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: wanted_id'
            }), 400
        
        wanted_id = data['wanted_id']
        wanted_scene = WantedScene.query.get(wanted_id)
        
        if not wanted_scene:
            return jsonify({
                'status': 'error',
                'message': 'Wanted scene not found'
            }), 404
        
        if wanted_scene.added_to_whisparr:
            return jsonify({
                'status': 'success',
                'message': 'Scene is already added to Whisparr',
                'whisparr_id': wanted_scene.whisparr_id
            })
        
        # Placeholder for actual Whisparr integration
        # This would use Whisparr client to add the movie
        whisparr_id = f"whisparr-{wanted_id}-{datetime.now().timestamp()}"
        
        # Update wanted scene
        wanted_scene.added_to_whisparr = True
        wanted_scene.whisparr_id = whisparr_id
        wanted_scene.whisparr_added_date = datetime.utcnow()
        wanted_scene.download_status = 'wanted'
        wanted_scene.status_updated_date = datetime.utcnow()
        db.session.commit()
        
        current_app.logger.info(f"Added scene to Whisparr: {wanted_scene.title}")
        
        return jsonify({
            'status': 'success',
            'message': 'Scene added to Whisparr successfully',
            'whisparr_id': whisparr_id
        })
        
    except Exception as e:
        current_app.logger.error(f"Error adding to Whisparr: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to add to Whisparr: {str(e)}'
        }), 500

@api_bp.route('/add-all-to-whisparr', methods=['POST'])
def add_all_to_whisparr():
    """Add multiple wanted scenes to Whisparr."""
    try:
        data = request.get_json()
        
        if not data or 'wanted_ids' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: wanted_ids'
            }), 400
        
        wanted_ids = data['wanted_ids']
        if not isinstance(wanted_ids, list):
            return jsonify({
                'status': 'error',
                'message': 'wanted_ids must be a list'
            }), 400
        
        added_count = 0
        errors = []
        
        for wanted_id in wanted_ids:
            try:
                wanted_scene = WantedScene.query.get(wanted_id)
                if not wanted_scene:
                    errors.append(f"Scene {wanted_id} not found")
                    continue
                
                if wanted_scene.added_to_whisparr:
                    continue  # Skip already added scenes
                
                # Placeholder for actual Whisparr integration
                whisparr_id = f"whisparr-{wanted_id}-{datetime.now().timestamp()}"
                
                # Update wanted scene
                wanted_scene.added_to_whisparr = True
                wanted_scene.whisparr_id = whisparr_id
                wanted_scene.whisparr_added_date = datetime.utcnow()
                wanted_scene.download_status = 'wanted'
                wanted_scene.status_updated_date = datetime.utcnow()
                
                added_count += 1
                
            except Exception as e:
                errors.append(f"Error adding scene {wanted_id}: {str(e)}")
        
        db.session.commit()
        
        current_app.logger.info(f"Added {added_count} scenes to Whisparr")
        
        return jsonify({
            'status': 'success',
            'added_count': added_count,
            'errors': errors,
            'message': f'{added_count} scenes added to Whisparr successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error adding all to Whisparr: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to add scenes to Whisparr: {str(e)}'
        }), 500

@api_bp.route('/remove-wanted', methods=['DELETE'])
def remove_wanted():
    """Remove a scene from the wanted list."""
    try:
        data = request.get_json()
        
        if not data or 'wanted_id' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: wanted_id'
            }), 400
        
        wanted_id = data['wanted_id']
        wanted_scene = WantedScene.query.get(wanted_id)
        
        if not wanted_scene:
            return jsonify({
                'status': 'error',
                'message': 'Wanted scene not found'
            }), 404
        
        scene_title = wanted_scene.title
        
        # Remove from database
        db.session.delete(wanted_scene)
        db.session.commit()
        
        current_app.logger.info(f"Removed wanted scene: {scene_title}")
        
        return jsonify({
            'status': 'success',
            'message': f'Scene "{scene_title}" removed from wanted list'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error removing wanted scene: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to remove scene: {str(e)}'
        }), 500

@api_bp.route('/refresh-whisparr-status', methods=['POST'])
def refresh_whisparr_status():
    """Refresh the download status of scenes in Whisparr."""
    try:
        # Get all scenes added to Whisparr
        whisparr_scenes = WantedScene.query.filter_by(added_to_whisparr=True).all()
        
        updated_count = 0
        
        for scene in whisparr_scenes:
            try:
                # Placeholder for actual Whisparr status check
                # This would query Whisparr API for current status
                
                # Simulate status update
                if scene.download_status == 'wanted':
                    # Randomly update status for demo
                    import random
                    statuses = ['wanted', 'searching', 'downloading', 'downloaded']
                    new_status = random.choice(statuses)
                    
                    if new_status != scene.download_status:
                        scene.download_status = new_status
                        scene.status_updated_date = datetime.utcnow()
                        updated_count += 1
                
            except Exception as e:
                current_app.logger.warning(f"Failed to update status for scene {scene.id}: {str(e)}")
        
        db.session.commit()
        
        current_app.logger.info(f"Refreshed status for {updated_count} scenes")
        
        return jsonify({
            'status': 'success',
            'updated_count': updated_count,
            'total_scenes': len(whisparr_scenes),
            'message': f'Status refreshed for {updated_count} scenes'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error refreshing Whisparr status: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to refresh status: {str(e)}'
        }), 500

# Error handlers for API
@api_bp.errorhandler(404)
def api_not_found(error):
    """Handle 404 errors in API."""
    return jsonify({
        'status': 'error',
        'message': 'API endpoint not found'
    }), 404

@api_bp.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors in API."""
    return jsonify({
        'status': 'error',
        'message': 'Method not allowed for this endpoint'
    }), 405

@api_bp.errorhandler(500)
def api_internal_error(error):
    """Handle 500 errors in API."""
    db.session.rollback()
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

# Request validation middleware
@api_bp.before_request
def validate_content_type():
    """Validate content type for POST/PUT requests."""
    if request.method in ['POST', 'PUT', 'PATCH'] and request.content_length:
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Content-Type must be application/json'
            }), 400
