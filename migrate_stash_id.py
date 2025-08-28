#!/usr/bin/env python3
"""
Database migration script to fix stash_id nullable constraint
Run this to update your existing database
"""

import sqlite3
import sys
import os

def run_migration(db_path):
    """Run the migration to make stash_id nullable"""
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Running database migration: Making stash_id nullable...")
        
        # Check if migration is needed
        cursor.execute("PRAGMA table_info(performers)")
        columns = cursor.fetchall()
        
        # Find stash_id column info
        stash_id_column = None
        for column in columns:
            if column[1] == 'stash_id':  # column[1] is the column name
                stash_id_column = column
                break
        
        if stash_id_column and stash_id_column[3] == 1:  # column[3] is notnull (1 = NOT NULL)
            print("Migration needed: stash_id is currently NOT NULL")
            
            # Create backup
            cursor.execute("CREATE TABLE performers_backup AS SELECT * FROM performers")
            cursor.execute("CREATE TABLE studios_backup AS SELECT * FROM studios")
            print("Created backup tables")
            
            # Performers table
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
            );
            """)
            
            # Copy data
            cursor.execute("""
            INSERT INTO performers_new (id, stash_id, stashdb_id, name, aliases, monitored, last_checked, created_date)
            SELECT id, stash_id, stashdb_id, name, aliases, monitored, last_checked, created_date
            FROM performers;
            """)
            
            # Drop old table and rename
            cursor.execute("DROP TABLE performers;")
            cursor.execute("ALTER TABLE performers_new RENAME TO performers;")
            print("Updated performers table")
            
            # Studios table
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
            );
            """)
            
            # Copy data
            cursor.execute("""
            INSERT INTO studios_new (id, stash_id, stashdb_id, name, parent_studio, monitored, last_checked, created_date)
            SELECT id, stash_id, stashdb_id, name, parent_studio, monitored, last_checked, created_date
            FROM studios;
            """)
            
            # Drop old table and rename
            cursor.execute("DROP TABLE studios;")
            cursor.execute("ALTER TABLE studios_new RENAME TO studios;")
            print("Updated studios table")
            
            # Commit changes
            conn.commit()
            print("✅ Migration completed successfully!")
            print("💾 Backup tables created: performers_backup, studios_backup")
            
        else:
            print("ℹ️  Migration not needed: stash_id is already nullable")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        sys.exit(1)

if __name__ == "__main__":
    # Try to find the database
    possible_paths = [
        "/app/data/stash_filter.db",
        "\\\\10.11.12.70\\appdata\\stash-filter\\data\\stash_filter.db",
        "./data/stash_filter.db"
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ Could not find database file. Please specify the path:")
        print("python migrate_stash_id.py /path/to/stash_filter.db")
        if len(sys.argv) > 1:
            db_path = sys.argv[1]
        else:
            sys.exit(1)
    
    print(f"🔍 Using database: {db_path}")
    run_migration(db_path)
