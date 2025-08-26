#!/usr/bin/env python3
"""
Migration Runner for Stash-Filter Database
Usage: python run_migration.py [migration_name] [action]
Actions: upgrade, downgrade, status
"""

import os
import sys
import importlib.util
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

def get_database_path():
    """Get the database path from environment or default."""
    return os.environ.get('DATABASE_PATH', '/app/data/stash_filter.db')

def load_migration(migration_name):
    """Load a migration module."""
    migration_file = app_dir / 'migrations' / f'{migration_name}.py'
    
    if not migration_file.exists():
        print(f"Migration {migration_name} not found")
        sys.exit(1)
    
    spec = importlib.util.spec_from_file_location(migration_name, migration_file)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    
    return migration

def list_migrations():
    """List all available migrations."""
    migrations_dir = app_dir / 'migrations'
    if not migrations_dir.exists():
        print("No migrations directory found")
        return []
    
    migrations = []
    for file in migrations_dir.glob('*.py'):
        if file.stem != '__init__':
            migrations.append(file.stem)
    
    return sorted(migrations)

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_migration.py [migration_name] [action]")
        print("       python run_migration.py list")
        print("\nActions: upgrade, downgrade, status")
        print("\nAvailable migrations:")
        for migration in list_migrations():
            print(f"  - {migration}")
        sys.exit(1)
    
    if sys.argv[1] == 'list':
        print("Available migrations:")
        for migration in list_migrations():
            print(f"  - {migration}")
        sys.exit(0)
    
    migration_name = sys.argv[1]
    action = sys.argv[2] if len(sys.argv) > 2 else 'status'
    
    # Set database path
    db_path = get_database_path()
    os.environ['DATABASE_PATH'] = db_path
    
    print(f"Using database: {db_path}")
    print(f"Running {action} for migration: {migration_name}")
    
    # Load and run migration
    migration = load_migration(migration_name)
    
    if action == 'upgrade':
        success = migration.upgrade_database(db_path)
        print(f"Migration {migration_name} upgrade: {'SUCCESS' if success else 'FAILED'}")
        sys.exit(0 if success else 1)
    
    elif action == 'downgrade':
        success = migration.downgrade_database(db_path)
        print(f"Migration {migration_name} downgrade: {'SUCCESS' if success else 'FAILED'}")
        sys.exit(0 if success else 1)
    
    elif action == 'status':
        applied = migration.check_migration_status(db_path)
        print(f"Migration {migration_name} status: {'APPLIED' if applied else 'NOT APPLIED'}")
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()
