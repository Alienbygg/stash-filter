from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import logging
from datetime import datetime

# Import custom modules
from .models import db, Performer, Studio, Scene, WantedScene, Config
from .stash_api import StashAPI
from .stashdb_api import StashDBAPI
from .whisparr_api import WhisparrAPI
from .scheduler import setup_scheduler

def create_app():
    # Set template and static folders relative to project root
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.environ.get('DATABASE_PATH', '/app/data/stash_filter.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, os.environ.get('LOG_LEVEL', 'INFO')),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize APIs
    stash_api = StashAPI()
    stashdb_api = StashDBAPI()
    whisparr_api = WhisparrAPI()
    
    # Routes
    @app.route('/')
    def index():
        """Main dashboard"""
        performers_count = Performer.query.filter_by(monitored=True).count()
        studios_count = Studio.query.filter_by(monitored=True).count()
        wanted_scenes_count = WantedScene.query.count()
        recent_scenes = Scene.query.order_by(Scene.discovered_date.desc()).limit(10).all()
        
        # Get last discovery run time
        last_scene = Scene.query.order_by(Scene.discovered_date.desc()).first()
        last_run_time = last_scene.discovered_date.strftime('%Y-%m-%d %H:%M') if last_scene else None
        
        return render_template('dashboard.html',
                             performers_count=performers_count,
                             studios_count=studios_count,
                             wanted_scenes_count=wanted_scenes_count,
                             recent_scenes=recent_scenes,
                             last_run_time=last_run_time)
    
    @app.route('/performers')
    def performers():
        """Performers management page"""
        performers = Performer.query.all()
        return render_template('performers.html', performers=performers)
    
    @app.route('/studios')
    def studios():
        """Studios management page"""
        studios = Studio.query.all()
        
        # Get recent studios activity (last 5 checked)
        recent_studios = (Studio.query
                         .filter(Studio.last_checked.isnot(None))
                         .order_by(Studio.last_checked.desc())
                         .limit(5)
                         .all())
        
        return render_template('studios.html', studios=studios, recent_studios=recent_studios)
    
    @app.route('/wanted-scenes')
    def wanted_scenes():
        """Wanted scenes list"""
        wanted = WantedScene.query.order_by(WantedScene.added_date.desc()).all()
        
        # Calculate scenes added in the last 7 days
        from datetime import datetime, timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        this_week_count = WantedScene.query.filter(WantedScene.added_date >= week_ago).count()
        
        return render_template('wanted_scenes.html', 
                             wanted_scenes=wanted, 
                             this_week_count=this_week_count)
    
    @app.route('/settings')
    def settings():
        """Settings page"""
        config = Config.get_config()
        
        # Pass environment variables to template - show actual values used by APIs
        env_vars = {
            'stash_url': os.environ.get('STASH_URL', 'http://10.11.12.70:6969'),
            'whisparr_url': os.environ.get('WHISPARR_URL', 'http://10.11.12.77:6969'),
            'stashdb_url': os.environ.get('STASHDB_URL', 'https://stashdb.org')
        }
        
        return render_template('settings.html', config=config, env_vars=env_vars)
    
    @app.route('/api/sync-favorites', methods=['POST'])
    def sync_favorites():
        """Sync favorites from Stash"""
        try:
            favorites = stash_api.get_favorites()
            
            # Sync performers
            for performer_data in favorites.get('performers', []):
                performer = Performer.query.filter_by(stash_id=performer_data['id']).first()
                if not performer:
                    performer = Performer(
                        stash_id=performer_data['id'],
                        name=performer_data['name'],
                        monitored=True
                    )
                    db.session.add(performer)
            
            # Sync studios
            for studio_data in favorites.get('studios', []):
                studio = Studio.query.filter_by(stash_id=studio_data['id']).first()
                if not studio:
                    studio = Studio(
                        stash_id=studio_data['id'],
                        name=studio_data['name'],
                        monitored=True
                    )
                    db.session.add(studio)
            
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Favorites synced successfully'})
            
        except Exception as e:
            app.logger.error(f"Error syncing favorites: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/toggle-monitoring', methods=['POST'])
    def toggle_monitoring():
        """Toggle monitoring for performer or studio"""
        data = request.json
        entity_type = data.get('type')  # 'performer' or 'studio'
        entity_id = data.get('id')
        
        try:
            if entity_type == 'performer':
                entity = Performer.query.get(entity_id)
            elif entity_type == 'studio':
                entity = Studio.query.get(entity_id)
            else:
                return jsonify({'status': 'error', 'message': 'Invalid entity type'}), 400
            
            if not entity:
                return jsonify({'status': 'error', 'message': 'Entity not found'}), 404
            
            entity.monitored = not entity.monitored
            db.session.commit()
            
            return jsonify({'status': 'success', 'monitored': entity.monitored})
            
        except Exception as e:
            app.logger.error(f"Error toggling monitoring: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/run-discovery', methods=['POST'])
    def run_discovery():
        """Manually trigger scene discovery"""
        try:
            from .discovery import run_discovery_task
            result = run_discovery_task()
            return jsonify(result)
            
        except Exception as e:
            app.logger.error(f"Error running discovery: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/save-settings', methods=['POST'])
    def save_settings():
        """Save application settings"""
        try:
            data = request.json
            config = Config.get_config()
            
            # Update configuration
            config.discovery_enabled = data.get('discovery_enabled', True)
            config.discovery_frequency_hours = data.get('discovery_frequency_hours', 24)
            config.max_scenes_per_check = data.get('max_scenes_per_check', 100)
            config.min_duration_minutes = data.get('min_duration_minutes', 0)
            config.max_duration_minutes = data.get('max_duration_minutes', 0)
            config.auto_add_to_whisparr = data.get('auto_add_to_whisparr', True)
            config.whisparr_quality_profile = data.get('whisparr_quality_profile', 'Any')
            
            # Update category filters
            config.set_unwanted_categories(data.get('unwanted_categories', []))
            config.set_required_categories(data.get('required_categories', []))
            
            db.session.commit()
            
            return jsonify({'status': 'success', 'message': 'Settings saved successfully'})
            
        except Exception as e:
            app.logger.error(f"Error saving settings: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/test-connections', methods=['POST'])
    def test_connections():
        """Test connections to external APIs"""
        try:
            results = {
                'stash': stash_api.test_connection(),
                'stashdb': stashdb_api.test_connection(),
                'whisparr': whisparr_api.test_connection()
            }
            return jsonify(results)
            
        except Exception as e:
            app.logger.error(f"Error testing connections: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/add-to-whisparr', methods=['POST'])
    def add_to_whisparr():
        """Add a wanted scene to Whisparr using StashDB UUID"""
        try:
            data = request.json
            wanted_id = data.get('wanted_id')
            
            wanted = WantedScene.query.get(wanted_id)
            if not wanted:
                return jsonify({'status': 'error', 'message': 'Wanted scene not found'}), 404
            
            if wanted.added_to_whisparr:
                return jsonify({'status': 'error', 'message': 'Scene already added to Whisparr'}), 400
            
            # Get the scene's StashDB UUID
            scene = wanted.scene
            if not scene or not scene.stashdb_id:
                return jsonify({'status': 'error', 'message': 'No StashDB ID found for this scene'}), 400
            
            # Check if already exists in Whisparr
            if whisparr_api.check_scene_exists_by_uuid(scene.stashdb_id):
                wanted.added_to_whisparr = True
                wanted.status = 'exists'
                db.session.commit()
                return jsonify({'status': 'success', 'message': 'Scene already exists in Whisparr'})
            
            # Add to Whisparr using UUID-based method
            result = whisparr_api.add_scene_by_uuid(scene.stashdb_id)
            
            if result:
                wanted.added_to_whisparr = True
                wanted.whisparr_id = str(result.get('id', ''))
                wanted.status = 'requested'
                db.session.commit()
                
                return jsonify({
                    'status': 'success', 
                    'message': f'Scene added to Whisparr successfully (ID: {result.get("id")})',
                    'whisparr_id': result.get('id')
                })
            else:
                return jsonify({'status': 'error', 'message': 'Failed to add scene to Whisparr'}), 500
            
        except Exception as e:
            app.logger.error(f"Error adding scene to Whisparr: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/add-all-to-whisparr', methods=['POST'])
    def add_all_to_whisparr():
        """Add multiple wanted scenes to Whisparr using StashDB UUIDs"""
        try:
            data = request.json
            wanted_ids = data.get('wanted_ids', [])
            
            if not wanted_ids:
                return jsonify({'status': 'error', 'message': 'No scenes selected'}), 400
            
            added_count = 0
            skipped_count = 0
            errors = []
            
            for wanted_id in wanted_ids:
                try:
                    wanted = WantedScene.query.get(wanted_id)
                    if not wanted or wanted.added_to_whisparr:
                        skipped_count += 1
                        continue
                    
                    # Get the scene's StashDB UUID
                    scene = wanted.scene
                    if not scene or not scene.stashdb_id:
                        errors.append(f"No StashDB ID for scene {wanted_id}: {wanted.title}")
                        continue
                    
                    # Check if already exists in Whisparr
                    if whisparr_api.check_scene_exists_by_uuid(scene.stashdb_id):
                        wanted.added_to_whisparr = True
                        wanted.status = 'exists'
                        skipped_count += 1
                        continue
                    
                    # Add to Whisparr using UUID-based method
                    result = whisparr_api.add_scene_by_uuid(scene.stashdb_id)
                    
                    if result:
                        wanted.added_to_whisparr = True
                        wanted.whisparr_id = str(result.get('id', ''))
                        wanted.status = 'requested'
                        added_count += 1
                    else:
                        errors.append(f"Failed to add scene {wanted_id}: {wanted.title}")
                    
                except Exception as e:
                    errors.append(f"Error adding scene {wanted_id}: {str(e)}")
            
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'added_count': added_count,
                'skipped_count': skipped_count,
                'message': f'Successfully added {added_count} scenes to Whisparr ({skipped_count} skipped)',
                'errors': errors
            })
            
        except Exception as e:
            app.logger.error(f"Error adding scenes to Whisparr: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/remove-wanted', methods=['DELETE'])
    def remove_wanted():
        """Remove a scene from the wanted list"""
        try:
            data = request.json
            wanted_id = data.get('wanted_id')
            
            wanted = WantedScene.query.get(wanted_id)
            if not wanted:
                return jsonify({'status': 'error', 'message': 'Wanted scene not found'}), 404
            
            # Also update the scene record
            if wanted.scene:
                wanted.scene.is_wanted = False
            
            db.session.delete(wanted)
            db.session.commit()
            
            return jsonify({'status': 'success', 'message': 'Scene removed from wanted list'})
            
        except Exception as e:
            app.logger.error(f"Error removing wanted scene: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/refresh-whisparr-status', methods=['POST'])
    def refresh_whisparr_status():
        """Refresh download status from Whisparr"""
        try:
            wanted_scenes = WantedScene.query.filter_by(added_to_whisparr=True).all()
            updated_count = 0
            
            for wanted in wanted_scenes:
                if wanted.whisparr_id:
                    try:
                        whisparr_movie = whisparr_api.get_download_status(int(wanted.whisparr_id))
                        if whisparr_movie:
                            # Update status based on Whisparr data
                            if whisparr_movie.get('hasFile'):
                                wanted.status = 'downloaded'
                                wanted.download_status = 'completed'
                            elif whisparr_movie.get('monitored'):
                                wanted.status = 'requested'
                                wanted.download_status = 'monitoring'
                            updated_count += 1
                    except Exception as e:
                        app.logger.error(f"Error updating status for scene {wanted.id}: {str(e)}")
            
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'updated_count': updated_count,
                'message': f'Status refreshed for {updated_count} scenes'
            })
            
        except Exception as e:
            app.logger.error(f"Error refreshing Whisparr status: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/get-stashdb-tags', methods=['GET'])
    def get_stashdb_tags():
        """Get all available tags from StashDB for category filtering"""
        try:
            tags = stashdb_api.get_all_tags()
            
            # Organize tags by category
            organized_tags = {}
            no_category_tags = []
            
            for tag in tags:
                tag_name = tag.get('name', 'Unknown')
                category = tag.get('category')
                
                if category and category.get('name'):
                    category_name = category['name']
                    if category_name not in organized_tags:
                        organized_tags[category_name] = []
                    organized_tags[category_name].append({
                        'id': tag.get('id'),
                        'name': tag_name,
                        'description': tag.get('description', '')
                    })
                else:
                    no_category_tags.append({
                        'id': tag.get('id'),
                        'name': tag_name,
                        'description': tag.get('description', '')
                    })
            
            # Add uncategorized tags if any
            if no_category_tags:
                organized_tags['Uncategorized'] = no_category_tags
            
            return jsonify({
                'status': 'success',
                'categories': organized_tags,
                'total_tags': len(tags)
            })
            
        except Exception as e:
            app.logger.error(f"Error fetching StashDB tags: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/cleanup-duplicates', methods=['POST'])
    def cleanup_duplicates():
        """Remove duplicate scenes and wanted scenes"""
        try:
            from .discovery import cleanup_duplicate_scenes
            result = cleanup_duplicate_scenes()
            return jsonify(result)
            
        except Exception as e:
            app.logger.error(f"Error cleaning up duplicates: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/whisparr-movie/<int:id>')
    def whisparr_movie(id):
        """Redirect to Whisparr movie page"""
        whisparr_url = os.environ.get('WHISPARR_URL', 'http://10.11.12.77:6969')
        return redirect(f"{whisparr_url}/movie/{id}")
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500
    
    # Initialize database tables
    with app.app_context():
        db.create_all()
        
        # Create default config if not exists
        if not Config.query.first():
            default_config = Config()
            db.session.add(default_config)
            db.session.commit()
    
    # Setup scheduler
    setup_scheduler()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=False)
