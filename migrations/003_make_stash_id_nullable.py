"""
Migration: Make stash_id nullable for manual performer/studio additions
Timestamp: 2025-08-28
"""

from alembic import op
import sqlalchemy as sa

def upgrade():
    """Make stash_id nullable for performers and studios"""
    
    # For SQLite, we need to recreate the table to change nullable constraints
    # Create new tables with correct schema
    
    # Performers table
    op.execute("""
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
    
    # Copy data from old table
    op.execute("""
    INSERT INTO performers_new (id, stash_id, stashdb_id, name, aliases, monitored, last_checked, created_date)
    SELECT id, stash_id, stashdb_id, name, aliases, monitored, last_checked, created_date
    FROM performers;
    """)
    
    # Drop old table and rename new one
    op.execute("DROP TABLE performers;")
    op.execute("ALTER TABLE performers_new RENAME TO performers;")
    
    # Studios table
    op.execute("""
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
    
    # Copy data from old table
    op.execute("""
    INSERT INTO studios_new (id, stash_id, stashdb_id, name, parent_studio, monitored, last_checked, created_date)
    SELECT id, stash_id, stashdb_id, name, parent_studio, monitored, last_checked, created_date
    FROM studios;
    """)
    
    # Drop old table and rename new one
    op.execute("DROP TABLE studios;")
    op.execute("ALTER TABLE studios_new RENAME TO studios;")
    
def downgrade():
    """Revert changes - make stash_id non-nullable again"""
    # This would require ensuring all records have stash_id values first
    pass
