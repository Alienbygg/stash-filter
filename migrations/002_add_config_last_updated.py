#!/usr/bin/env python3
"""
Migration: Add last_updated column to config table
Version: 002
Date: 2025-08-27
Description: Add missing last_updated column to config table to fix schema mismatch
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
        
        logger.info("Starting migration 002: Add last_updated column to config table")
        
        # Check if config table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='config'
        """)
        
        if not cursor.fetchone():
            logger.info("Config table doesn't exist, creating it")
            # Create the full config table with all columns
            cursor.execute("""
                CREATE TABLE config (
                    id INTEGER PRIMARY KEY,
                    unwanted_categories TEXT DEFAULT '[]',
                    required_categories TEXT DEFAULT '[]',
                    discovery_enabled BOOLEAN DEFAULT 1,
                    discovery_frequency_hours INTEGER DEFAULT 24,
                    max_scenes_per_check INTEGER DEFAULT 100,
                    min_duration_minutes INTEGER DEFAULT 0,
                    max_duration_minutes INTEGER DEFAULT 0,
                    auto_add_to_whisparr BOOLEAN DEFAULT 1,
                    whisparr_quality_profile VARCHAR(100) DEFAULT 'Any',
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("Created config table with all columns")
            
            # Insert default config
            cursor.execute("""
                INSERT INTO config (
                    unwanted_categories, 
                    required_categories,
                    discovery_enabled,
                    discovery_frequency_hours,
                    max_scenes_per_check,
                    min_duration_minutes,
                    max_duration_minutes,
                    auto_add_to_whisparr,
                    whisparr_quality_profile
                ) VALUES (
                    '[]', '[]', 1, 24, 100, 0, 0, 1, 'Any'
                )
            """)
            logger.info("Inserted default configuration")
        else:
            # Check if last_updated column exists
            cursor.execute("PRAGMA table_info(config)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'last_updated' not in columns:
                logger.info("Adding last_updated column to config table")
                cursor.execute("""
                    ALTER TABLE config 
                    ADD COLUMN last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                """)
                
                # Update existing rows to have the current timestamp
                cursor.execute("""
                    UPDATE config 
                    SET last_updated = CURRENT_TIMESTAMP 
                    WHERE last_updated IS NULL
                """)
                logger.info("Added last_updated column and updated existing records")
            else:
                logger.info("last_updated column already exists")
        
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
            VALUES ('002', 'add_config_last_updated', ?, 1)
        """, (datetime.utcnow().isoformat(),))
        
        conn.commit()
        logger.info("Migration 002 completed successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Migration 002 failed: {str(e)}")
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
        
        logger.info("Starting rollback of migration 002")
        
        # SQLite doesn't support DROP COLUMN, so we need to recreate the table
        # Check if last_updated column exists
        cursor.execute("PRAGMA table_info(config)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'last_updated' in columns:
            logger.info("Recreating config table without last_updated column")
            
            # Create temporary table without last_updated
            cursor.execute("""
                CREATE TABLE config_temp (
                    id INTEGER PRIMARY KEY,
                    unwanted_categories TEXT DEFAULT '[]',
                    required_categories TEXT DEFAULT '[]',
                    discovery_enabled BOOLEAN DEFAULT 1,
                    discovery_frequency_hours INTEGER DEFAULT 24,
                    max_scenes_per_check INTEGER DEFAULT 100,
                    min_duration_minutes INTEGER DEFAULT 0,
                    max_duration_minutes INTEGER DEFAULT 0,
                    auto_add_to_whisparr BOOLEAN DEFAULT 1,
                    whisparr_quality_profile VARCHAR(100) DEFAULT 'Any',
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Copy data (excluding last_updated)
            cursor.execute("""
                INSERT INTO config_temp (
                    id, unwanted_categories, required_categories, discovery_enabled,
                    discovery_frequency_hours, max_scenes_per_check, min_duration_minutes,
                    max_duration_minutes, auto_add_to_whisparr, whisparr_quality_profile,
                    created_date
                )
                SELECT 
                    id, unwanted_categories, required_categories, discovery_enabled,
                    discovery_frequency_hours, max_scenes_per_check, min_duration_minutes,
                    max_duration_minutes, auto_add_to_whisparr, whisparr_quality_profile,
                    created_date
                FROM config
            """)
            
            # Replace original table
            cursor.execute("DROP TABLE config")
            cursor.execute("ALTER TABLE config_temp RENAME TO config")
            
            logger.info("Removed last_updated column from config table")
        
        # Remove migration record
        cursor.execute("DELETE FROM migration_history WHERE version = '002'")
        
        conn.commit()
        logger.info("Migration 002 rollback completed successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Migration 002 rollback failed: {str(e)}")
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
            # If no migration history, check if last_updated column exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='config'
            """)
            
            if cursor.fetchone():
                cursor.execute("PRAGMA table_info(config)")
                columns = [column[1] for column in cursor.fetchall()]
                return 'last_updated' in columns
            return False
        
        # Check if this migration has been applied
        cursor.execute("""
            SELECT COUNT(*) FROM migration_history 
            WHERE version = '002' AND success = 1
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
        print("Usage: python 002_add_config_last_updated.py [upgrade|downgrade|status]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "upgrade":
        if check_migration_status(db_path):
            print("Migration 002 already applied")
        else:
            success = upgrade_database(db_path)
            print("Migration 002 applied successfully" if success else "Migration 002 failed")
            sys.exit(0 if success else 1)
    
    elif command == "downgrade":
        if not check_migration_status(db_path):
            print("Migration 002 not applied, nothing to rollback")
        else:
            success = downgrade_database(db_path)
            print("Migration 002 rollback successful" if success else "Migration 002 rollback failed")
            sys.exit(0 if success else 1)
    
    elif command == "status":
        applied = check_migration_status(db_path)
        print(f"Migration 002 status: {'Applied' if applied else 'Not Applied'}")
    
    else:
        print("Invalid command. Use: upgrade, downgrade, or status")
        sys.exit(1)
