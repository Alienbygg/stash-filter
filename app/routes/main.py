"""
Main web routes for Stash-Filter application.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app import db
from app.models import Performer, Studio, Scene, WantedScene, Config, DiscoveryLog, FilteredScene

# Create blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main dashboard page."""
    try:
        # Get summary statistics
        performer_count = Performer.query.filter_by(monitored=True).count()
        studio_count = Studio.query.filter_by(monitored=True).count()
        wanted_count = WantedScene.query.filter_by(status='wanted').count()
        
        # Get recent discovery log
        recent_discovery = DiscoveryLog.query.order_by(DiscoveryLog.started_date.desc()).first()
        
        # Get recent wanted scenes
        recent_wanted = WantedScene.query.order_by(WantedScene.added_date.desc()).limit(10).all()
        
        return render_template('index.html', 
                             performer_count=performer_count,
                             studio_count=studio_count,
                             wanted_count=wanted_count,
                             recent_discovery=recent_discovery,
                             recent_wanted=recent_wanted)
    except Exception as e:
        # Fallback for missing database tables during initial setup
        return render_template('index.html',
                             performer_count=0,
                             studio_count=0, 
                             wanted_count=0,
                             recent_discovery=None,
                             recent_wanted=[])

@main_bp.route('/performers')
def performers():
    """Performers management page."""
    page = request.args.get('page', 1, type=int)
    per_page = 25
    
    # Filter by monitoring status if requested
    monitored_filter = request.args.get('monitored')
    query = Performer.query
    
    if monitored_filter == 'true':
        query = query.filter_by(monitored=True)
    elif monitored_filter == 'false':
        query = query.filter_by(monitored=False)
    
    # Search functionality
    search = request.args.get('search', '')
    if search:
        query = query.filter(Performer.name.contains(search))
    
    performers = query.order_by(Performer.name).paginate(
        page=page, per_page=per_page, error_out=False)
    
    return render_template('performers.html', 
                         performers=performers,
                         search=search,
                         monitored_filter=monitored_filter)

@main_bp.route('/studios')
def studios():
    """Studios management page."""
    page = request.args.get('page', 1, type=int)
    per_page = 25
    
    # Filter by monitoring status if requested
    monitored_filter = request.args.get('monitored')
    query = Studio.query
    
    if monitored_filter == 'true':
        query = query.filter_by(monitored=True)
    elif monitored_filter == 'false':
        query = query.filter_by(monitored=False)
    
    # Search functionality
    search = request.args.get('search', '')
    if search:
        query = query.filter(Studio.name.contains(search))
    
    studios = query.order_by(Studio.name).paginate(
        page=page, per_page=per_page, error_out=False)
    
    return render_template('studios.html',
                         studios=studios,
                         search=search,
                         monitored_filter=monitored_filter)

@main_bp.route('/wanted-scenes')
def wanted_scenes():
    """Wanted scenes page."""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Filter by status
    status_filter = request.args.get('status')
    query = WantedScene.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    # Filter by Whisparr status
    whisparr_filter = request.args.get('whisparr')
    if whisparr_filter == 'added':
        query = query.filter_by(added_to_whisparr=True)
    elif whisparr_filter == 'not_added':
        query = query.filter_by(added_to_whisparr=False)
    
    # Search functionality
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            db.or_(
                WantedScene.title.contains(search),
                WantedScene.performer_name.contains(search),
                WantedScene.studio_name.contains(search)
            )
        )
    
    wanted_scenes = query.order_by(WantedScene.added_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    
    return render_template('wanted_scenes.html',
                         wanted_scenes=wanted_scenes,
                         search=search,
                         status_filter=status_filter,
                         whisparr_filter=whisparr_filter)

@main_bp.route('/settings')
def settings():
    """Settings page."""
    config = Config.query.first()
    
    # Create default config if none exists
    if not config:
        config = Config()
        db.session.add(config)
        db.session.commit()
    
    return render_template('settings.html', config=config)

@main_bp.route('/filtered-scenes')
def filtered_scenes():
    """Filtered scenes management page."""
    return render_template('filtered_scenes.html')

@main_bp.route('/logs')
def logs():
    """Discovery logs page."""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    logs = DiscoveryLog.query.order_by(DiscoveryLog.started_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    
    return render_template('logs.html', logs=logs)

@main_bp.route('/about')
def about():
    """About page."""
    from app import __version__
    return render_template('about.html', version=__version__)

# Error handlers
@main_bp.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('errors/404.html'), 404

@main_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    db.session.rollback()
    return render_template('errors/500.html'), 500

# Template context processors
@main_bp.context_processor
def inject_navigation():
    """Inject navigation data into all templates."""
    try:
        # Get counts for navigation badges
        performer_count = Performer.query.filter_by(monitored=True).count()
        studio_count = Studio.query.filter_by(monitored=True).count()
        wanted_count = WantedScene.query.filter_by(status='wanted').count()
        filtered_count = FilteredScene.query.filter_by(is_exception=False).count()
        
        return dict(
            nav_performer_count=performer_count,
            nav_studio_count=studio_count,
            nav_wanted_count=wanted_count,
            nav_filtered_count=filtered_count
        )
    except Exception:
        # Return zeros if database not ready
        return dict(
            nav_performer_count=0,
            nav_studio_count=0,
            nav_wanted_count=0,
            nav_filtered_count=0
        )

@main_bp.context_processor
def inject_config():
    """Inject configuration data into templates."""
    try:
        config = Config.query.first()
        return dict(app_config=config)
    except Exception:
        return dict(app_config=None)

# Template filters
@main_bp.app_template_filter('datetime_format')
def datetime_format(datetime_obj, format='%Y-%m-%d %H:%M'):
    """Format datetime for templates."""
    if datetime_obj:
        return datetime_obj.strftime(format)
    return ''

@main_bp.app_template_filter('duration_format')
def duration_format(seconds):
    """Format duration in seconds to readable format."""
    if not seconds:
        return ''
    
    minutes = seconds // 60
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if hours > 0:
        return f"{hours}h {remaining_minutes}m"
    else:
        return f"{minutes}m"

@main_bp.app_template_filter('status_badge_class')
def status_badge_class(status):
    """Get Bootstrap badge class for status."""
    status_classes = {
        'wanted': 'badge-primary',
        'searching': 'badge-warning',
        'downloading': 'badge-info',
        'downloaded': 'badge-success',
        'failed': 'badge-danger'
    }
    return status_classes.get(status, 'badge-secondary')
