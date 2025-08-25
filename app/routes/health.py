"""
Health check routes for Stash-Filter application.
"""

from flask import Blueprint, jsonify, current_app
from datetime import datetime
import os
import psutil
from app import db, __version__
from app.models import Config, DiscoveryLog

# Create blueprint
health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    """Basic health check endpoint."""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': __version__
        })
    except Exception as e:
        current_app.logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 503

@health_bp.route('/health/detailed')
def detailed_health_check():
    """Detailed health check with system metrics."""
    try:
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': __version__,
            'checks': {}
        }
        
        # Database check
        try:
            db.session.execute('SELECT 1')
            health_data['checks']['database'] = {
                'status': 'healthy',
                'message': 'Database connection successful'
            }
        except Exception as e:
            health_data['checks']['database'] = {
                'status': 'unhealthy',
                'message': f'Database connection failed: {str(e)}'
            }
            health_data['status'] = 'unhealthy'
        
        # Configuration check
        try:
            config = Config.query.first()
            if config:
                health_data['checks']['configuration'] = {
                    'status': 'healthy',
                    'message': 'Configuration loaded'
                }
            else:
                health_data['checks']['configuration'] = {
                    'status': 'warning',
                    'message': 'No configuration found'
                }
        except Exception as e:
            health_data['checks']['configuration'] = {
                'status': 'unhealthy',
                'message': f'Configuration check failed: {str(e)}'
            }
        
        # Disk space check
        try:
            disk_usage = psutil.disk_usage('/')
            disk_percent = (disk_usage.used / disk_usage.total) * 100
            
            if disk_percent < 80:
                health_data['checks']['disk_space'] = {
                    'status': 'healthy',
                    'usage_percent': round(disk_percent, 2),
                    'free_gb': round(disk_usage.free / (1024**3), 2)
                }
            elif disk_percent < 90:
                health_data['checks']['disk_space'] = {
                    'status': 'warning',
                    'usage_percent': round(disk_percent, 2),
                    'free_gb': round(disk_usage.free / (1024**3), 2),
                    'message': 'Disk space usage is high'
                }
            else:
                health_data['checks']['disk_space'] = {
                    'status': 'unhealthy',
                    'usage_percent': round(disk_percent, 2),
                    'free_gb': round(disk_usage.free / (1024**3), 2),
                    'message': 'Disk space usage is critical'
                }
                health_data['status'] = 'unhealthy'
        except Exception as e:
            health_data['checks']['disk_space'] = {
                'status': 'unknown',
                'message': f'Disk check failed: {str(e)}'
            }
        
        # Memory check
        try:
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            if memory_percent < 80:
                health_data['checks']['memory'] = {
                    'status': 'healthy',
                    'usage_percent': memory_percent,
                    'available_gb': round(memory.available / (1024**3), 2)
                }
            elif memory_percent < 90:
                health_data['checks']['memory'] = {
                    'status': 'warning',
                    'usage_percent': memory_percent,
                    'available_gb': round(memory.available / (1024**3), 2),
                    'message': 'Memory usage is high'
                }
            else:
                health_data['checks']['memory'] = {
                    'status': 'unhealthy',
                    'usage_percent': memory_percent,
                    'available_gb': round(memory.available / (1024**3), 2),
                    'message': 'Memory usage is critical'
                }
        except Exception as e:
            health_data['checks']['memory'] = {
                'status': 'unknown',
                'message': f'Memory check failed: {str(e)}'
            }
        
        # Recent discovery check
        try:
            recent_discovery = DiscoveryLog.query.order_by(
                DiscoveryLog.started_date.desc()
            ).first()
            
            if recent_discovery:
                time_since_last = datetime.utcnow() - recent_discovery.started_date
                hours_since = time_since_last.total_seconds() / 3600
                
                if hours_since < 48:  # Less than 48 hours
                    health_data['checks']['recent_discovery'] = {
                        'status': 'healthy',
                        'last_run': recent_discovery.started_date.isoformat(),
                        'last_status': recent_discovery.status,
                        'hours_ago': round(hours_since, 1)
                    }
                else:
                    health_data['checks']['recent_discovery'] = {
                        'status': 'warning',
                        'last_run': recent_discovery.started_date.isoformat(),
                        'last_status': recent_discovery.status,
                        'hours_ago': round(hours_since, 1),
                        'message': 'No recent discovery runs'
                    }
            else:
                health_data['checks']['recent_discovery'] = {
                    'status': 'warning',
                    'message': 'No discovery runs found'
                }
        except Exception as e:
            health_data['checks']['recent_discovery'] = {
                'status': 'unknown',
                'message': f'Discovery check failed: {str(e)}'
            }
        
        # Overall status determination
        check_statuses = [check['status'] for check in health_data['checks'].values()]
        if 'unhealthy' in check_statuses:
            health_data['status'] = 'unhealthy'
            status_code = 503
        elif 'warning' in check_statuses:
            health_data['status'] = 'degraded'
            status_code = 200
        else:
            health_data['status'] = 'healthy'
            status_code = 200
        
        return jsonify(health_data), status_code
        
    except Exception as e:
        current_app.logger.error(f"Detailed health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 503

@health_bp.route('/health/ready')
def readiness_check():
    """Kubernetes readiness probe endpoint."""
    try:
        # Check if application is ready to serve requests
        
        # Test database connection
        db.session.execute('SELECT 1')
        
        # Check if basic configuration exists
        config = Config.query.first()
        if not config:
            # Create default configuration if none exists
            config = Config()
            db.session.add(config)
            db.session.commit()
        
        return jsonify({
            'status': 'ready',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Readiness check failed: {str(e)}")
        return jsonify({
            'status': 'not_ready',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 503

@health_bp.route('/health/live')
def liveness_check():
    """Kubernetes liveness probe endpoint."""
    try:
        # Basic liveness check - just ensure the app is responding
        return jsonify({
            'status': 'alive',
            'timestamp': datetime.utcnow().isoformat(),
            'uptime_seconds': psutil.Process(os.getpid()).create_time()
        })
        
    except Exception as e:
        current_app.logger.error(f"Liveness check failed: {str(e)}")
        return jsonify({
            'status': 'not_alive',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 503

@health_bp.route('/metrics')
def metrics():
    """Prometheus-style metrics endpoint."""
    try:
        from app.models import Performer, Studio, Scene, WantedScene
        
        # Get database counts
        performer_count = Performer.query.count()
        monitored_performer_count = Performer.query.filter_by(monitored=True).count()
        studio_count = Studio.query.count()
        monitored_studio_count = Studio.query.filter_by(monitored=True).count()
        scene_count = Scene.query.count()
        wanted_scene_count = WantedScene.query.count()
        
        # Get system metrics
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cpu_percent = psutil.cpu_percent()
        
        # Generate Prometheus-style metrics
        metrics_text = f"""# HELP stash_filter_performers_total Total number of performers
# TYPE stash_filter_performers_total gauge
stash_filter_performers_total {performer_count}

# HELP stash_filter_performers_monitored Number of monitored performers
# TYPE stash_filter_performers_monitored gauge
stash_filter_performers_monitored {monitored_performer_count}

# HELP stash_filter_studios_total Total number of studios
# TYPE stash_filter_studios_total gauge
stash_filter_studios_total {studio_count}

# HELP stash_filter_studios_monitored Number of monitored studios
# TYPE stash_filter_studios_monitored gauge
stash_filter_studios_monitored {monitored_studio_count}

# HELP stash_filter_scenes_total Total number of discovered scenes
# TYPE stash_filter_scenes_total gauge
stash_filter_scenes_total {scene_count}

# HELP stash_filter_wanted_scenes_total Total number of wanted scenes
# TYPE stash_filter_wanted_scenes_total gauge
stash_filter_wanted_scenes_total {wanted_scene_count}

# HELP stash_filter_memory_usage_percent Memory usage percentage
# TYPE stash_filter_memory_usage_percent gauge
stash_filter_memory_usage_percent {memory.percent}

# HELP stash_filter_disk_usage_percent Disk usage percentage
# TYPE stash_filter_disk_usage_percent gauge
stash_filter_disk_usage_percent {(disk.used / disk.total) * 100:.2f}

# HELP stash_filter_cpu_usage_percent CPU usage percentage
# TYPE stash_filter_cpu_usage_percent gauge
stash_filter_cpu_usage_percent {cpu_percent}
"""
        
        return metrics_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}
        
    except Exception as e:
        current_app.logger.error(f"Metrics collection failed: {str(e)}")
        return f"# Error collecting metrics: {str(e)}", 500, {'Content-Type': 'text/plain; charset=utf-8'}

@health_bp.route('/version')
def version_info():
    """Version information endpoint."""
    try:
        return jsonify({
            'version': __version__,
            'build_date': '2025-01-20',  # This would be set during build
            'git_commit': 'unknown',     # This would be set during build
            'python_version': os.sys.version,
            'platform': os.uname().system if hasattr(os, 'uname') else 'unknown'
        })
        
    except Exception as e:
        current_app.logger.error(f"Version info failed: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500
