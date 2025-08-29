#!/usr/bin/env python3
"""
Migration: Make stash_id nullable for manual performer/studio additions
Version: 003
Date: 2025-08-28
Description: Update performers and studios tables to make stash_id nullable, allowing manual additions from StashDB
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
        
        logger.info("Starting migration 003: Make stash_id nullable")
        
        # Check if migration is needed by inspecting current schema
        cursor.execute("PRAGMA table_info(performers)")
        performers_columns = cursor.fetchall()
        
        # Find stash_id column info
        stash_id_column = None
        for column in performers_columns:
            if column[1] == 'stash_id':  # column[1] is the column name
                stash_id_column = column
                break
        
        if stash_id_column and stash_id_column[3] == 1:  # column[3] is notnull (1 = NOT NULL)
            logger.info("Migration needed: stash_id is currently NOT NULL")
            
            # Create backup tables first
            cursor.execute("CREATE TABLE performers_backup AS SELECT * FROM performers")
            cursor.execute("CREATE TABLE studios_backup AS SELECT * FROM studios") 
            logger.info("Created backup tables: performers_backup, studios_backup")
            
            # Create new performers table with nullable stash_id
            cursor.execute("""
            CREATE TABLE performers_new (
                id INTEGER NOT NULL,
                stash_id VARCHAR(50),
                stashdb_id VARCHAR(50),
                name VARCHAR(200) NOT NULL,
                aliases TEXT,
                monitored BOOLEAN DEFAULT 1,
                last_checked DATETIME DEFAULT (datetime('now')),
                created_date DATETIME DEFAULT (datetime('now')),
                PRIMARY KEY (id),
                UNIQUE (stashdb_id)
            )
            """)
            
            # Copy data from old table
            cursor.execute("""
            INSERT INTO performers_new (id, stash_id, stashdb_id, name, aliases, monitored, last_checked, created_date)
            SELECT id, stash_id, stashdb_id, name, aliases, monitored, last_checked, created_date
            FROM performers
            """)
            
            # Drop old table and rename new one
            cursor.execute("DROP TABLE performers")
            cursor.execute("ALTER TABLE performers_new RENAME TO performers")
            logger.info("Updated performers table schema")
            
            # Create new studios table with nullable stash_id
            cursor.execute("""
            CREATE TABLE studios_new (
                id INTEGER NOT NULL,
                stash_id VARCHAR(50),
                stashdb_id VARCHAR(50),
                name VARCHAR(200) NOT NULL,
                parent_studio VARCHAR(200),
                monitored BOOLEAN DEFAULT 1,
                last_checked DATETIME DEFAULT (datetime('now')),
                created_date DATETIME DEFAULT (datetime('now')),
                PRIMARY KEY (id),
                UNIQUE (stashdb_id)
            )
            """)
            
            # Copy data from old table
            cursor.execute("""
            INSERT INTO studios_new (id, stash_id, stashdb_id, name, parent_studio, monitored, last_checked, created_date)
            SELECT id, stash_id, stashdb_id, name, parent_studio, monitored, last_checked, created_date
            FROM studios
            """)
            
            # Drop old table and rename new one
            cursor.execute("DROP TABLE studios")
            cursor.execute("ALTER TABLE studios_new RENAME TO studios")
            logger.info("Updated studios table schema")
            
        else:
            logger.info("Migration not needed: stash_id is already nullable")
        
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
            VALUES ('003', 'make_stash_id_nullable', ?, 1)
        """, (datetime.utcnow().isoformat(),))
        
        conn.commit()
        logger.info("Migration 003 completed successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Migration 003 failed: {str(e)}")
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
        
        logger.info("Starting rollback of migration 003")
        logger.warning("Downgrade not implemented - would require making stash_id NOT NULL again")
        logger.warning("This could fail if there are records with NULL stash_id values")
        logger.info("If you need to rollback, restore from backup tables: performers_backup, studios_backup")
        
        # Remove migration record
        cursor.execute("DELETE FROM migration_history WHERE version = '003'")
        
        conn.commit()
        logger.info("Migration 003 rollback record removed")
        
        return True
        
    except Exception as e:
        logger.error(f"Migration 003 rollback failed: {str(e)}")
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
            WHERE version = '003' AND success = 1
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
        print("Usage: python 003_make_stash_id_nullable.py [upgrade|downgrade|status]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "upgrade":
        if check_migration_status(db_path):
            print("Migration 003 already applied")
        else:
            success = upgrade_database(db_path)
            print("Migration 003 applied successfully" if success else "Migration 003 failed")
            sys.exit(0 if success else 1)
    
    elif command == "downgrade":
        if not check_migration_status(db_path):
            print("Migration 003 not applied, nothing to rollback")
        else:
            success = downgrade_database(db_path)
            print("Migration 003 rollback successful" if success else "Migration 003 rollback failed")
            sys.exit(0 if success else 1)
    
    elif command == "status":
        applied = check_migration_status(db_path)
        print(f"Migration 003 status: {'Applied' if applied else 'Not Applied'}")
    
    else:
        print("Invalid command. Use: upgrade, downgrade, or status")
        sys.exit(1)
