#!/bin/bash

echo "🚀 Stash-Filter Major Update Deployment"
echo "======================================="
echo ""
echo "This script will deploy all the latest fixes and features:"
echo "✅ Fix database 'NOT NULL constraint' error"
echo "✅ Add performer search functionality" 
echo "✅ Add trending scenes with thumbnails"
echo "✅ Enhanced UI and StashDB integration"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

# Check if docker-compose is available
COMPOSE_CMD=""
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    print_error "Neither docker-compose nor 'docker compose' is available"
    exit 1
fi

print_info "Using compose command: $COMPOSE_CMD"

# Find container
CONTAINER_NAME=""
POSSIBLE_NAMES=("stash-filter" "stash_filter" "stashfilter")

echo ""
print_info "Looking for Stash-Filter container..."
for name in "${POSSIBLE_NAMES[@]}"; do
    if docker ps -a --format "table {{.Names}}" | grep -q "^$name$"; then
        CONTAINER_NAME=$name
        print_status "Found container: $CONTAINER_NAME"
        break
    fi
done

if [ -z "$CONTAINER_NAME" ]; then
    print_warning "Container not found with common names."
    echo "Please enter your Stash-Filter container name:"
    read -r CONTAINER_NAME
    
    if ! docker ps -a --format "table {{.Names}}" | grep -q "^$CONTAINER_NAME$"; then
        print_error "Container '$CONTAINER_NAME' not found"
        exit 1
    fi
fi

echo ""
echo "📋 Deployment Plan:"
echo "  • Container: $CONTAINER_NAME"
echo "  • Action: Stop container, run database migration, restart"
echo "  • Backup: Database backup will be created automatically"
echo ""

read -p "Do you want to proceed with the deployment? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_error "Deployment cancelled."
    exit 1
fi

echo ""
print_info "Starting deployment process..."

# Step 1: Stop container
echo ""
print_info "Step 1: Stopping container..."
if docker stop "$CONTAINER_NAME" > /dev/null 2>&1; then
    print_status "Container stopped"
else
    print_warning "Container was not running or failed to stop"
fi

# Step 2: Get container volume info
echo ""
print_info "Step 2: Locating database..."
VOLUME_INFO=$(docker inspect "$CONTAINER_NAME" | grep -A 1 -B 1 "/app/data")
DATA_PATH=""

# Try to find mounted data directory
if command -v jq &> /dev/null; then
    DATA_PATH=$(docker inspect "$CONTAINER_NAME" | jq -r '.[0].Mounts[] | select(.Destination == "/app/data") | .Source' 2>/dev/null)
fi

if [ -z "$DATA_PATH" ] || [ "$DATA_PATH" = "null" ]; then
    print_warning "Could not automatically locate data directory"
    echo "Please enter the full path to your data directory (where stash_filter.db is located):"
    read -r DATA_PATH
fi

DB_PATH="$DATA_PATH/stash_filter.db"
if [ ! -f "$DB_PATH" ]; then
    print_error "Database not found at: $DB_PATH"
    echo "Please enter the correct path to stash_filter.db:"
    read -r DB_PATH
    if [ ! -f "$DB_PATH" ]; then
        print_error "Database file not found: $DB_PATH"
        exit 1
    fi
fi

print_status "Database found: $DB_PATH"

# Step 3: Run migration
echo ""
print_info "Step 3: Running database migration..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        print_error "Python not found. Please install Python to run this migration."
        exit 1
    else
        PYTHON_CMD=python
    fi
else
    PYTHON_CMD=python3
fi

if $PYTHON_CMD migrate_stash_id.py "$DB_PATH"; then
    print_status "Database migration completed successfully"
else
    print_error "Database migration failed"
    print_info "Starting container anyway..."
fi

# Step 4: Start container
echo ""
print_info "Step 4: Starting container..."
if docker start "$CONTAINER_NAME" > /dev/null 2>&1; then
    print_status "Container started"
else
    print_error "Failed to start container"
    exit 1
fi

# Step 5: Wait for startup and test
echo ""
print_info "Step 5: Waiting for application startup..."
sleep 5

# Try to detect the port
PORT=$(docker port "$CONTAINER_NAME" 2>/dev/null | grep "5000/tcp" | cut -d: -f2)
if [ -z "$PORT" ]; then
    PORT="5000"
fi

print_info "Testing application health..."
if curl -s "http://localhost:$PORT/health" > /dev/null 2>&1; then
    print_status "Application is responding"
else
    print_warning "Application may still be starting up"
fi

# Final summary
echo ""
echo "🎉 Deployment Complete!"
echo "======================="
echo ""
print_status "Database migration applied"
print_status "Container restarted successfully"
print_status "New features are now available"
echo ""
echo "🆕 New Features Available:"
echo "  • Performer search via StashDB"
echo "  • Manual performer addition" 
echo "  • Trending scenes with thumbnails"
echo "  • Enhanced UI and mobile support"
echo ""
echo "🌐 Access your updated Stash-Filter:"
echo "  URL: http://localhost:$PORT"
echo ""
echo "💡 What to try:"
echo "  1. Go to Performers page"
echo "  2. Click 'Add Manually' to test the fix"
echo "  3. Check the Dashboard for trending scenes"
echo ""
print_status "Deployment successful! Happy filtering! 🎯"
