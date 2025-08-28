"""
Database Migration: Make stash_id nullable for manual additions
Migration: manual_additions_nullable_stash_id
Version: 1.2.0
Date: 2025-08-28
"""

import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def migrate_up(db_path):
    """
    Make stash_id nullable for performers and studios to support manual additions
    """
    logger.info("Starting migration: Make stash_id nullable for manual additions")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create backup tables first
        logger.info("Creating backup tables...")
        
        cursor.execute("""
            CREATE TABLE performers_backup AS 
            SELECT * FROM performers
        """)
        
        cursor.execute("""
            CREATE TABLE studios_backup AS 
            SELECT * FROM studios
        """)
        
        # Drop the original tables
        logger.info("Dropping original tables...")
        cursor.execute("DROP TABLE performers")
        cursor.execute("DROP TABLE studios")
        
        # Recreate performers table with nullable stash_id
        logger.info("Recreating performers table with nullable stash_id...")
        cursor.execute("""
            CREATE TABLE performers (
                id INTEGER PRIMARY KEY,
                stash_id VARCHAR(50),  -- Now nullable, no unique constraint
                stashdb_id VARCHAR(50) UNIQUE,
                name VARCHAR(200) NOT NULL,
                aliases TEXT,
                monitored BOOLEAN DEFAULT 1,
                last_checked DATETIME DEFAULT (datetime('now')),
                created_date DATETIME DEFAULT (datetime('now'))
            )
        """)
        
        # Recreate studios table with nullable stash_id  
        logger.info("Recreating studios table with nullable stash_id...")
        cursor.execute("""
            CREATE TABLE studios (
                id INTEGER PRIMARY KEY,
                stash_id VARCHAR(50),  -- Now nullable, no unique constraint
                stashdb_id VARCHAR(50) UNIQUE,
                name VARCHAR(200) NOT NULL,
                parent_studio VARCHAR(200),
                monitored BOOLEAN DEFAULT 1,
                last_checked DATETIME DEFAULT (datetime('now')),
                created_date DATETIME DEFAULT (datetime('now'))
            )
        """)
        
        # Copy data back from backup tables
        logger.info("Copying data back from backups...")
        cursor.execute("""
            INSERT INTO performers (id, stash_id, stashdb_id, name, aliases, monitored, last_checked, created_date)
            SELECT id, stash_id, stashdb_id, name, aliases, monitored, last_checked, created_date
            FROM performers_backup
        """)
        
        cursor.execute("""
            INSERT INTO studios (id, stash_id, stashdb_id, name, parent_studio, monitored, last_checked, created_date)
            SELECT id, stash_id, stashdb_id, name, parent_studio, monitored, last_checked, created_date
            FROM studios_backup
        """)
        
        # Drop backup tables
        logger.info("Cleaning up backup tables...")
        cursor.execute("DROP TABLE performers_backup")
        cursor.execute("DROP TABLE studios_backup")
        
        # Create unique index on stash_id where not null (partial unique index)
        logger.info("Creating partial unique indexes...")
        cursor.execute("""
            CREATE UNIQUE INDEX idx_performers_stash_id_unique 
            ON performers(stash_id) WHERE stash_id IS NOT NULL
        """)
        
        cursor.execute("""
            CREATE UNIQUE INDEX idx_studios_stash_id_unique 
            ON studios(stash_id) WHERE stash_id IS NOT NULL
        """)
        
        conn.commit()
        logger.info("Migration completed successfully!")
        
        # Verify the migration
        cursor.execute("SELECT COUNT(*) FROM performers")
        performers_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM studios")
        studios_count = cursor.fetchone()[0]
        
        logger.info(f"Migration verified: {performers_count} performers, {studios_count} studios")
        
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        conn.rollback()
        
        # Try to restore from backup if it exists
        try:
            logger.info("Attempting to restore from backup...")
            cursor.execute("DROP TABLE IF EXISTS performers")
            cursor.execute("DROP TABLE IF EXISTS studios")
            cursor.execute("ALTER TABLE performers_backup RENAME TO performers")
            cursor.execute("ALTER TABLE studios_backup RENAME TO studios")
            conn.commit()
            logger.info("Restored from backup")
        except:
            logger.error("Failed to restore from backup")
        
        return False
        
    finally:
        conn.close()

def migrate_down(db_path):
    """
    Rollback: Make stash_id required again (only if all stash_id values are not null)
    """
    logger.info("Starting rollback: Make stash_id required again")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if any performers/studios have null stash_id
        cursor.execute("SELECT COUNT(*) FROM performers WHERE stash_id IS NULL")
        null_performers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM studios WHERE stash_id IS NULL")
        null_studios = cursor.fetchone()[0]
        
        if null_performers > 0 or null_studios > 0:
            logger.error(f"Cannot rollback: {null_performers} performers and {null_studios} studios have null stash_id")
            logger.error("Remove manually added performers/studios first, or provide stash_id values")
            return False
        
        # If no nulls, we can safely recreate with NOT NULL constraint
        # (Implementation would be similar to migrate_up but with NOT NULL constraint)
        logger.info("Rollback would be safe, but not implemented")
        return False
        
    except Exception as e:
        logger.error(f"Rollback failed: {str(e)}")
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    # For testing
    migrate_up("/app/data/stash_filter.db")
