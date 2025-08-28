#!/bin/bash

echo "🔧 Stash-Filter Database Migration Script"
echo "========================================="
echo ""
echo "This will fix the database error you're experiencing by making"
echo "the 'stash_id' field nullable for manual performer additions."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Python not found. Please install Python to run this migration."
        exit 1
    else
        PYTHON_CMD=python
    fi
else
    PYTHON_CMD=python3
fi

echo "🐍 Using Python: $PYTHON_CMD"
echo ""

# Find the database file
DB_PATH=""

# Common paths to check
PATHS=(
    "/app/data/stash_filter.db"
    "./data/stash_filter.db" 
    "/appdata/stash-filter/data/stash_filter.db"
    "\\\\10.11.12.70\\appdata\\stash-filter\\data\\stash_filter.db"
)

echo "🔍 Searching for database..."
for path in "${PATHS[@]}"; do
    if [ -f "$path" ]; then
        DB_PATH="$path"
        echo "✅ Found database: $DB_PATH"
        break
    fi
done

if [ -z "$DB_PATH" ]; then
    echo "❓ Database not found in common locations."
    echo "Please enter the full path to your stash_filter.db file:"
    read -r DB_PATH
    
    if [ ! -f "$DB_PATH" ]; then
        echo "❌ File not found: $DB_PATH"
        exit 1
    fi
fi

echo ""
echo "📋 Migration Summary:"
echo "  • Database: $DB_PATH"
echo "  • Action: Make stash_id nullable for performers and studios"
echo "  • Backup: Will create backup tables automatically"
echo ""

read -p "Do you want to proceed? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Migration cancelled."
    exit 1
fi

echo ""
echo "🚀 Running migration..."
$PYTHON_CMD migrate_stash_id.py "$DB_PATH"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Migration completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Restart your Stash-Filter Docker container"
    echo "2. Try adding a performer using the 'Add Manually' button"
    echo "3. The database error should now be fixed!"
    echo ""
    echo "💡 Tip: You can now search and add performers from StashDB"
    echo "   without needing them in your local Stash instance."
else
    echo ""
    echo "❌ Migration failed. Check the error messages above."
    echo "Your original database is still intact."
    exit 1
fi
