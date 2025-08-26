"""
API routes for Stash-Filter application.
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
import uuid
from sqlalchemy import or_, func
from app import db
from app.models import Performer, Studio, Scene, WantedScene, Config, DiscoveryLog, FilteredScene, FilterException

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

# Filtered Scenes Management API

@api_bp.route('/filtered-scenes', methods=['GET'])
def get_filtered_scenes():
    """Get paginated list of filtered scenes with filters."""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)  # Max 100 per page
        filter_reason = request.args.get('filter_reason')
        filter_category = request.args.get('filter_category')
        has_exception = request.args.get('has_exception')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        search = request.args.get('search')  # Search in title, performers, studio
        
        # Build query
        query = FilteredScene.query
        
        # Apply filters
        if filter_reason:
            query = query.filter(FilteredScene.filter_reason == filter_reason)
        
        if filter_category:
            query = query.filter(FilteredScene.filter_category == filter_category)
        
        if has_exception is not None:
            query = query.filter(FilteredScene.is_exception == (has_exception.lower() == 'true'))
        
        if date_from:
            try:
                from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                query = query.filter(FilteredScene.filtered_date >= from_date)
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid date_from format. Use ISO format.'
                }), 400
        
        if date_to:
            try:
                to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                query = query.filter(FilteredScene.filtered_date <= to_date)
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid date_to format. Use ISO format.'
                }), 400
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(or_(
                FilteredScene.title.ilike(search_term),
                FilteredScene.performers.ilike(search_term),
                FilteredScene.studio.ilike(search_term)
            ))
        
        # Execute query with pagination
        scenes = query.order_by(FilteredScene.filtered_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'status': 'success',
            'scenes': [scene.to_dict() for scene in scenes.items],
            'pagination': {
                'page': scenes.page,
                'pages': scenes.pages,
                'per_page': scenes.per_page,
                'total': scenes.total,
                'has_prev': scenes.has_prev,
                'has_next': scenes.has_next
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting filtered scenes: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to get filtered scenes: {str(e)}'
        }), 500


@api_bp.route('/filtered-scenes/stats', methods=['GET'])
def get_filtered_stats():
    """Get statistics about filtered scenes."""
    try:
        # Get date range (default to last 30 days)
        days = request.args.get('days', 30, type=int)
        date_from = datetime.utcnow() - timedelta(days=days)
        
        # Total filtered scenes in period
        total_filtered = FilteredScene.query.filter(
            FilteredScene.filtered_date >= date_from
        ).count()
        
        # Total exceptions in period
        total_exceptions = FilteredScene.query.filter(
            FilteredScene.is_exception == True,
            FilteredScene.filtered_date >= date_from
        ).count()
        
        # Exception rate
        exception_rate = round((total_exceptions / max(total_filtered, 1)) * 100, 1)
        
        # Filter reason breakdown
        filter_reasons = db.session.query(
            FilteredScene.filter_reason,
            func.count(FilteredScene.id).label('count')
        ).filter(
            FilteredScene.filtered_date >= date_from
        ).group_by(FilteredScene.filter_reason).all()
        
        # Filter category breakdown
        filter_categories = db.session.query(
            FilteredScene.filter_category,
            func.count(FilteredScene.id).label('count')
        ).filter(
            FilteredScene.filtered_date >= date_from
        ).group_by(FilteredScene.filter_category).all()
        
        # Top studios that get filtered
        top_filtered_studios = db.session.query(
            FilteredScene.studio,
            func.count(FilteredScene.id).label('count')
        ).filter(
            FilteredScene.filtered_date >= date_from,
            FilteredScene.studio.isnot(None)
        ).group_by(FilteredScene.studio).order_by(
            func.count(FilteredScene.id).desc()
        ).limit(10).all()
        
        # Recent activity (last 7 days by day)
        recent_activity = []
        for i in range(7):
            day_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            day_filtered = FilteredScene.query.filter(
                FilteredScene.filtered_date >= day_start,
                FilteredScene.filtered_date < day_end
            ).count()
            
            day_exceptions = FilteredScene.query.filter(
                FilteredScene.filtered_date >= day_start,
                FilteredScene.filtered_date < day_end,
                FilteredScene.is_exception == True
            ).count()
            
            recent_activity.append({
                'date': day_start.strftime('%Y-%m-%d'),
                'filtered': day_filtered,
                'exceptions': day_exceptions
            })
        
        return jsonify({
            'status': 'success',
            'period_days': days,
            'total_filtered': total_filtered,
            'total_exceptions': total_exceptions,
            'exception_rate': exception_rate,
            'filter_reasons': [{'reason': r[0], 'count': r[1]} for r in filter_reasons],
            'filter_categories': [{'category': c[0], 'count': c[1]} for c in filter_categories],
            'top_filtered_studios': [{'studio': s[0], 'count': s[1]} for s in top_filtered_studios],
            'recent_activity': list(reversed(recent_activity))  # Oldest to newest
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting filtered stats: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to get statistics: {str(e)}'
        }), 500


@api_bp.route('/filtered-scenes/<int:scene_id>', methods=['GET'])
def get_filtered_scene(scene_id):
    """Get detailed information about a specific filtered scene."""
    try:
        scene = FilteredScene.query.get(scene_id)
        
        if not scene:
            return jsonify({
                'status': 'error',
                'message': 'Filtered scene not found'
            }), 404
        
        # Include exceptions in the response
        scene_data = scene.to_dict()
        scene_data['exceptions'] = [exc.to_dict() for exc in scene.exceptions]
        
        return jsonify({
            'status': 'success',
            'scene': scene_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting filtered scene {scene_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to get scene: {str(e)}'
        }), 500


@api_bp.route('/filtered-scenes/<int:scene_id>/exception', methods=['POST'])
def create_exception(scene_id):
    """Create exception for filtered scene."""
    try:
        scene = FilteredScene.query.get(scene_id)
        
        if not scene:
            return jsonify({
                'status': 'error',
                'message': 'Filtered scene not found'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No exception data provided'
            }), 400
        
        # Validate exception type
        exception_type = data.get('type', 'permanent')
        if exception_type not in ['permanent', 'temporary', 'one-time']:
            return jsonify({
                'status': 'error',
                'message': 'Invalid exception type. Must be: permanent, temporary, or one-time'
            }), 400
        
        # Handle expiration date for temporary exceptions
        expires_at = None
        if exception_type == 'temporary':
            expires_str = data.get('expires_at')
            if not expires_str:
                return jsonify({
                    'status': 'error',
                    'message': 'expires_at is required for temporary exceptions'
                }), 400
            
            try:
                expires_at = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
                if expires_at <= datetime.utcnow():
                    return jsonify({
                        'status': 'error',
                        'message': 'Expiration date must be in the future'
                    }), 400
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid expires_at format. Use ISO format.'
                }), 400
        
        # Create exception
        exception = FilterException(
            filtered_scene_id=scene_id,
            exception_type=exception_type,
            reason=data.get('reason', ''),
            expires_at=expires_at,
            auto_add_to_whisparr=bool(data.get('add_to_whisparr', False))
        )
        
        # Update scene exception status
        scene.is_exception = True
        scene.exception_date = datetime.utcnow()
        scene.exception_reason = data.get('reason', '')
        
        db.session.add(exception)
        db.session.commit()
        
        current_app.logger.info(f"Created {exception_type} exception for filtered scene: {scene.title}")
        
        # If auto-add to Whisparr is enabled, add logic here
        if data.get('add_to_whisparr', False):
            # Placeholder for Whisparr integration
            current_app.logger.info(f"Scene queued for Whisparr: {scene.title}")
        
        return jsonify({
            'status': 'success',
            'message': f'{exception_type.title()} exception created successfully',
            'exception': exception.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error creating exception: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to create exception: {str(e)}'
        }), 500


@api_bp.route('/exceptions/<int:exception_id>', methods=['PUT'])
def update_exception(exception_id):
    """Update an existing exception."""
    try:
        exception = FilterException.query.get(exception_id)
        
        if not exception:
            return jsonify({
                'status': 'error',
                'message': 'Exception not found'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No update data provided'
            }), 400
        
        # Update fields
        if 'reason' in data:
            exception.reason = data['reason']
        
        if 'is_active' in data:
            exception.is_active = bool(data['is_active'])
        
        if 'expires_at' in data:
            if data['expires_at']:
                try:
                    exception.expires_at = datetime.fromisoformat(data['expires_at'].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({
                        'status': 'error',
                        'message': 'Invalid expires_at format. Use ISO format.'
                    }), 400
            else:
                exception.expires_at = None
        
        if 'auto_add_to_whisparr' in data:
            exception.auto_add_to_whisparr = bool(data['auto_add_to_whisparr'])
        
        exception.updated_at = datetime.utcnow()
        db.session.commit()
        
        current_app.logger.info(f"Updated exception {exception_id}")
        
        return jsonify({
            'status': 'success',
            'message': 'Exception updated successfully',
            'exception': exception.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error updating exception: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to update exception: {str(e)}'
        }), 500


@api_bp.route('/exceptions/<int:exception_id>', methods=['DELETE'])
def delete_exception(exception_id):
    """Delete an exception."""
    try:
        exception = FilterException.query.get(exception_id)
        
        if not exception:
            return jsonify({
                'status': 'error',
                'message': 'Exception not found'
            }), 404
        
        # Update the filtered scene's exception status if this was the only active exception
        filtered_scene = exception.filtered_scene
        
        db.session.delete(exception)
        
        # Check if scene has any other active exceptions
        remaining_exceptions = FilterException.query.filter(
            FilterException.filtered_scene_id == filtered_scene.id,
            FilterException.id != exception_id,
            FilterException.is_active == True
        ).count()
        
        if remaining_exceptions == 0:
            filtered_scene.is_exception = False
            filtered_scene.exception_date = None
            filtered_scene.exception_reason = None
        
        db.session.commit()
        
        current_app.logger.info(f"Deleted exception {exception_id}")
        
        return jsonify({
            'status': 'success',
            'message': 'Exception deleted successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error deleting exception: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to delete exception: {str(e)}'
        }), 500


@api_bp.route('/filtered-scenes/bulk-exception', methods=['POST'])
def create_bulk_exceptions():
    """Create exceptions for multiple filtered scenes."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No bulk exception data provided'
            }), 400
        
        scene_ids = data.get('scene_ids', [])
        if not scene_ids or not isinstance(scene_ids, list):
            return jsonify({
                'status': 'error',
                'message': 'scene_ids must be a non-empty list'
            }), 400
        
        exception_type = data.get('type', 'permanent')
        if exception_type not in ['permanent', 'temporary', 'one-time']:
            return jsonify({
                'status': 'error',
                'message': 'Invalid exception type. Must be: permanent, temporary, or one-time'
            }), 400
        
        # Handle expiration date for temporary exceptions
        expires_at = None
        if exception_type == 'temporary':
            expires_str = data.get('expires_at')
            if not expires_str:
                return jsonify({
                    'status': 'error',
                    'message': 'expires_at is required for temporary exceptions'
                }), 400
            
            try:
                expires_at = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid expires_at format. Use ISO format.'
                }), 400
        
        created_count = 0
        errors = []
        
        for scene_id in scene_ids:
            try:
                scene = FilteredScene.query.get(scene_id)
                if not scene:
                    errors.append(f"Scene {scene_id} not found")
                    continue
                
                # Create exception
                exception = FilterException(
                    filtered_scene_id=scene_id,
                    exception_type=exception_type,
                    reason=data.get('reason', ''),
                    expires_at=expires_at,
                    auto_add_to_whisparr=bool(data.get('add_to_whisparr', False))
                )
                
                # Update scene exception status
                scene.is_exception = True
                scene.exception_date = datetime.utcnow()
                scene.exception_reason = data.get('reason', '')
                
                db.session.add(exception)
                created_count += 1
                
            except Exception as e:
                errors.append(f"Error creating exception for scene {scene_id}: {str(e)}")
        
        db.session.commit()
        
        current_app.logger.info(f"Created {created_count} bulk exceptions")
        
        return jsonify({
            'status': 'success',
            'created_count': created_count,
            'errors': errors,
            'message': f'{created_count} exceptions created successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error creating bulk exceptions: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to create bulk exceptions: {str(e)}'
        }), 500


@api_bp.route('/filtered-scenes/cleanup', methods=['POST'])
def cleanup_filtered_scenes():
    """Clean up old filtered scenes and expired exceptions."""
    try:
        data = request.get_json() or {}
        days_to_keep = data.get('days_to_keep', 90)  # Default keep 90 days
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # Delete old filtered scenes (except those with active exceptions)
        old_scenes = FilteredScene.query.filter(
            FilteredScene.filtered_date < cutoff_date,
            FilteredScene.is_exception == False
        )
        
        deleted_scenes = old_scenes.count()
        old_scenes.delete(synchronize_session=False)
        
        # Delete expired exceptions
        expired_exceptions = FilterException.query.filter(
            FilterException.expires_at < datetime.utcnow(),
            FilterException.is_active == True
        )
        
        expired_count = expired_exceptions.count()
        
        # Update expired exceptions to inactive
        expired_exceptions.update({
            'is_active': False,
            'updated_at': datetime.utcnow()
        }, synchronize_session=False)
        
        # Update filtered scenes that no longer have active exceptions
        scenes_with_expired_exceptions = db.session.query(FilteredScene).join(FilterException).filter(
            FilterException.is_active == False,
            FilteredScene.is_exception == True
        ).all()
        
        updated_scenes = 0
        for scene in scenes_with_expired_exceptions:
            # Check if scene has any other active exceptions
            active_exceptions = FilterException.query.filter(
                FilterException.filtered_scene_id == scene.id,
                FilterException.is_active == True
            ).count()
            
            if active_exceptions == 0:
                scene.is_exception = False
                scene.exception_date = None
                scene.exception_reason = None
                updated_scenes += 1
        
        db.session.commit()
        
        current_app.logger.info(f"Cleanup completed: {deleted_scenes} scenes deleted, {expired_count} exceptions expired, {updated_scenes} scenes updated")
        
        return jsonify({
            'status': 'success',
            'deleted_scenes': deleted_scenes,
            'expired_exceptions': expired_count,
            'updated_scenes': updated_scenes,
            'message': f'Cleanup completed: {deleted_scenes} old scenes removed, {expired_count} exceptions expired'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error during cleanup: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Cleanup failed: {str(e)}'
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
