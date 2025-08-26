from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import os
from datetime import datetime

from .discovery import run_discovery_task
from .models import db, LogEntry

logger = logging.getLogger(__name__)

def setup_scheduler():
    """Setup the background scheduler for daily tasks"""
    scheduler = BackgroundScheduler()
    
    # Daily discovery task - runs at 6 AM
    scheduler.add_job(
        func=scheduled_discovery,
        trigger=CronTrigger(hour=6, minute=0),
        id='daily_discovery',
        name='Daily Scene Discovery',
        replace_existing=True
    )
    
    # Weekly cleanup task - runs on Sundays at 2 AM
    scheduler.add_job(
        func=scheduled_cleanup,
        trigger=CronTrigger(day_of_week=6, hour=2, minute=0),
        id='weekly_cleanup',
        name='Weekly Database Cleanup',
        replace_existing=True
    )
    
    try:
        scheduler.start()
        logger.info("Scheduler started successfully")
        log_message("INFO", "Scheduler started successfully", "scheduler")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}")
        log_message("ERROR", f"Failed to start scheduler: {str(e)}", "scheduler")

def scheduled_discovery():
    """Scheduled task for daily scene discovery"""
    logger.info("Starting scheduled discovery task")
    log_message("INFO", "Starting scheduled discovery task", "scheduler")
    
    try:
        result = run_discovery_task()
        
        # Log the results
        message = f"Discovery completed: {result.get('new_scenes', 0)} new scenes, {result.get('wanted_added', 0)} added to wanted list"
        logger.info(message)
        log_message("INFO", message, "discovery")
        
    except Exception as e:
        error_msg = f"Scheduled discovery failed: {str(e)}"
        logger.error(error_msg)
        log_message("ERROR", error_msg, "discovery")

def scheduled_cleanup():
    """Scheduled task for weekly database cleanup"""
    logger.info("Starting scheduled cleanup task")
    log_message("INFO", "Starting scheduled cleanup task", "scheduler")
    
    try:
        from .models import Scene, WantedScene, LogEntry
        from datetime import datetime, timedelta
        
        cleanup_count = 0
        
        # Clean up old log entries (keep only last 30 days)
        old_logs = LogEntry.query.filter(
            LogEntry.timestamp < datetime.utcnow() - timedelta(days=30)
        ).all()
        
        for log in old_logs:
            db.session.delete(log)
            cleanup_count += 1
        
        # Clean up filtered scenes older than 90 days
        old_filtered_scenes = Scene.query.filter(
            Scene.is_filtered == True,
            Scene.discovered_date < datetime.utcnow() - timedelta(days=90)
        ).all()
        
        for scene in old_filtered_scenes:
            # Also remove associated wanted entries
            wanted_entries = WantedScene.query.filter_by(scene_id=scene.id).all()
            for wanted in wanted_entries:
                db.session.delete(wanted)
            
            db.session.delete(scene)
            cleanup_count += 1
        
        db.session.commit()
        
        message = f"Cleanup completed: {cleanup_count} records removed"
        logger.info(message)
        log_message("INFO", message, "cleanup")
        
    except Exception as e:
        error_msg = f"Scheduled cleanup failed: {str(e)}"
        logger.error(error_msg)
        log_message("ERROR", error_msg, "cleanup")

def manual_discovery():
    """Manually trigger discovery task"""
    logger.info("Manual discovery triggered")
    log_message("INFO", "Manual discovery triggered", "manual")
    
    try:
        result = run_discovery_task()
        return result
    except Exception as e:
        error_msg = f"Manual discovery failed: {str(e)}"
        logger.error(error_msg)
        log_message("ERROR", error_msg, "discovery")
        raise

def log_message(level: str, message: str, module: str = None):
    """Log a message to the database"""
    try:
        log_entry = LogEntry(
            level=level,
            message=message,
            module=module,
            timestamp=datetime.utcnow()
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        logger.error(f"Failed to log message to database: {str(e)}")

# Standalone script for cron execution
if __name__ == "__main__":
    # This allows the script to be run directly by cron
    import sys
    import os
    
    # Add the app directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Set up Flask app context
    from app.main import create_app
    
    app = create_app()
    
    with app.app_context():
        if len(sys.argv) > 1 and sys.argv[1] == 'cleanup':
            scheduled_cleanup()
        else:
            scheduled_discovery()
