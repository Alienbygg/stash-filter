"""
Fix stash_id to be nullable in performers table
"""
import sqlite3
import logging
import os

logger = logging.getLogger(__name__)

def upgrade_database(db_path):
    """Make stash_id nullable in performers table"""
    try:
        logger.info(f"Running migration 004: Fix stash_id nullable in {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if performers table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='performers'")
        if not cursor.fetchone():
            logger.info("Performers table doesn't exist yet, skipping migration")
            conn.close()
            return True
        
        # Create new table with nullable stash_id
        cursor.execute('''
            CREATE TABLE performers_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stash_id TEXT NULL,
                stashdb_id TEXT,
                name TEXT NOT NULL,
                aliases TEXT,
                monitored BOOLEAN DEFAULT 0,
                last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Copy data from old table
        cursor.execute('''
            INSERT INTO performers_new (id, stash_id, stashdb_id, name, aliases, monitored, last_checked, created_date)
            SELECT id, stash_id, stashdb_id, name, aliases, monitored, last_checked, created_date
            FROM performers
        ''')
        
        # Drop old table and rename new one
        cursor.execute('DROP TABLE performers')
        cursor.execute('ALTER TABLE performers_new RENAME TO performers')
        
        conn.commit()
        conn.close()
        
        logger.info("Migration 004 completed: stash_id is now nullable")
        return True
        
    except Exception as e:
        logger.error(f"Migration 004 failed: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def downgrade_database(db_path):
    """Downgrade not supported for this migration"""
    pass
