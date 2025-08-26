#!/usr/bin/env python3
"""
Migration: Add filtered scenes and exceptions tables
Version: 001
Date: 2025-08-25
Description: Add filtered_scenes and filter_exceptions tables for tracking filtered scenes and exceptions
"""

import sqlite3
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def upgrade_database(db_path):
    """Apply the migration to upgrade the database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        logger.info("Starting migration 001: Add filtered scenes tables")
        
        # Create filtered_scenes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS filtered_scenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stash_id VARCHAR(50),
                stashdb_id VARCHAR(100),
                title VARCHAR(500) NOT NULL,
                performers TEXT,
                studio VARCHAR(200),
                tags TEXT,
                duration INTEGER,
                release_date VARCHAR(20),
                filter_reason VARCHAR(100) NOT NULL,
                filter_category VARCHAR(50) NOT NULL,
                filter_details TEXT,
                scene_url VARCHAR(500),
                thumbnail_url VARCHAR(500),
                is_exception BOOLEAN DEFAULT 0 NOT NULL,
                exception_date DATETIME,
                exception_reason VARCHAR(500),
                filtered_date DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
            )
        """)
        
        logger.info("Created filtered_scenes table")
        
        # Create filter_exceptions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS filter_exceptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filtered_scene_id INTEGER NOT NULL,
                exception_type VARCHAR(50) NOT NULL,
                reason VARCHAR(500),
                created_by VARCHAR(100) DEFAULT 'user' NOT NULL,
                expires_at DATETIME,
                is_active BOOLEAN DEFAULT 1 NOT NULL,
                times_used INTEGER DEFAULT 0 NOT NULL,
                last_used_date DATETIME,
                auto_add_to_whisparr BOOLEAN DEFAULT 0 NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                FOREIGN KEY (filtered_scene_id) REFERENCES filtered_scenes (id) ON DELETE CASCADE
            )
        """)
        
        logger.info("Created filter_exceptions table")
        
        # Create indexes for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_filtered_scenes_filtered_date 
            ON filtered_scenes (filtered_date)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_filtered_scenes_filter_reason 
            ON filtered_scenes (filter_reason)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_filtered_scenes_is_exception 
            ON filtered_scenes (is_exception)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_filtered_scenes_stash_id 
            ON filtered_scenes (stash_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_filter_exceptions_scene_id 
            ON filter_exceptions (filtered_scene_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_filter_exceptions_is_active 
            ON filter_exceptions (is_active)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_filter_exceptions_expires_at 
            ON filter_exceptions (expires_at)
        """)
        
        logger.info("Created database indexes")
        
        # Create migration tracking table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS migration_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version VARCHAR(10) NOT NULL,
                name VARCHAR(200) NOT NULL,
                applied_date DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                success BOOLEAN DEFAULT 1 NOT NULL
            )
        """)
        
        # Record this migration
        cursor.execute("""
            INSERT OR IGNORE INTO migration_history (version, name, applied_date, success)
            VALUES ('001', 'add_filtered_scenes', ?, 1)
        """, (datetime.utcnow().isoformat(),))
        
        conn.commit()
        logger.info("Migration 001 completed successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Migration 001 failed: {str(e)}")
        conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close()


def downgrade_database(db_path):
    """Rollback the migration (downgrade the database)."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        logger.info("Starting rollback of migration 001")
        
        # Drop indexes
        cursor.execute("DROP INDEX IF EXISTS idx_filter_exceptions_expires_at")
        cursor.execute("DROP INDEX IF EXISTS idx_filter_exceptions_is_active")
        cursor.execute("DROP INDEX IF EXISTS idx_filter_exceptions_scene_id")
        cursor.execute("DROP INDEX IF EXISTS idx_filtered_scenes_stash_id")
        cursor.execute("DROP INDEX IF EXISTS idx_filtered_scenes_is_exception")
        cursor.execute("DROP INDEX IF EXISTS idx_filtered_scenes_filter_reason")
        cursor.execute("DROP INDEX IF EXISTS idx_filtered_scenes_filtered_date")
        
        # Drop tables (foreign key constraints will handle cascade)
        cursor.execute("DROP TABLE IF EXISTS filter_exceptions")
        cursor.execute("DROP TABLE IF EXISTS filtered_scenes")
        
        # Remove migration record
        cursor.execute("DELETE FROM migration_history WHERE version = '001'")
        
        conn.commit()
        logger.info("Migration 001 rollback completed successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Migration 001 rollback failed: {str(e)}")
        conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close()


def check_migration_status(db_path):
    """Check if this migration has been applied."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if migration_history table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='migration_history'
        """)
        
        if not cursor.fetchone():
            return False
        
        # Check if this migration has been applied
        cursor.execute("""
            SELECT COUNT(*) FROM migration_history 
            WHERE version = '001' AND success = 1
        """)
        
        result = cursor.fetchone()
        return result[0] > 0 if result else False
        
    except Exception as e:
        logger.error(f"Error checking migration status: {str(e)}")
        return False
        
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    import sys
    import os
    
    # Default database path
    db_path = os.environ.get('DATABASE_PATH', '/app/data/stash_filter.db')
    
    if len(sys.argv) < 2:
        print("Usage: python 001_add_filtered_scenes.py [upgrade|downgrade|status]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "upgrade":
        if check_migration_status(db_path):
            print("Migration 001 already applied")
        else:
            success = upgrade_database(db_path)
            print("Migration 001 applied successfully" if success else "Migration 001 failed")
            sys.exit(0 if success else 1)
    
    elif command == "downgrade":
        if not check_migration_status(db_path):
            print("Migration 001 not applied, nothing to rollback")
        else:
            success = downgrade_database(db_path)
            print("Migration 001 rollback successful" if success else "Migration 001 rollback failed")
            sys.exit(0 if success else 1)
    
    elif command == "status":
        applied = check_migration_status(db_path)
        print(f"Migration 001 status: {'Applied' if applied else 'Not Applied'}")
    
    else:
        print("Invalid command. Use: upgrade, downgrade, or status")
        sys.exit(1)
