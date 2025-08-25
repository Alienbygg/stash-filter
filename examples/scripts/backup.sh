#!/bin/bash
# Stash-Filter Backup Script
# Creates daily backups of database and configuration

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-./backups}"
DATA_DIR="${DATA_DIR:-./data}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

log "Starting Stash-Filter backup..."

# Check if database exists
if [ ! -f "$DATA_DIR/stash_filter.db" ]; then
    error "Database file not found at $DATA_DIR/stash_filter.db"
    exit 1
fi

# Create database backup
log "Backing up database..."
if command -v sqlite3 >/dev/null 2>&1; then
    sqlite3 "$DATA_DIR/stash_filter.db" ".backup $BACKUP_DIR/stash_filter_$TIMESTAMP.db"
    log "Database backup created: stash_filter_$TIMESTAMP.db"
else
    # Fallback to file copy if sqlite3 not available
    warn "sqlite3 command not found, using file copy"
    cp "$DATA_DIR/stash_filter.db" "$BACKUP_DIR/stash_filter_$TIMESTAMP.db"
fi

# Backup configuration files
log "Backing up configuration..."
if [ -f "$DATA_DIR/config.json" ]; then
    cp "$DATA_DIR/config.json" "$BACKUP_DIR/config_$TIMESTAMP.json"
fi

# Backup environment file if exists
if [ -f ".env" ]; then
    # Remove sensitive data from env backup
    grep -v -E "(API_KEY|SECRET_KEY|PASSWORD)" .env > "$BACKUP_DIR/env_$TIMESTAMP.txt" || true
fi

# Create comprehensive backup archive
log "Creating archive backup..."
tar -czf "$BACKUP_DIR/stash_filter_full_$TIMESTAMP.tar.gz" \
    -C "$DATA_DIR" . \
    --exclude='*.log' \
    --exclude='*.tmp' \
    --exclude='cache/*' 2>/dev/null || true

# Cleanup old backups
log "Cleaning up old backups (older than $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "stash_filter_*.db" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
find "$BACKUP_DIR" -name "config_*.json" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
find "$BACKUP_DIR" -name "env_*.txt" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
find "$BACKUP_DIR" -name "stash_filter_full_*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true

# Verify backup integrity
log "Verifying backup integrity..."
if command -v sqlite3 >/dev/null 2>&1; then
    if sqlite3 "$BACKUP_DIR/stash_filter_$TIMESTAMP.db" "PRAGMA integrity_check;" | grep -q "ok"; then
        log "Database backup integrity verified"
    else
        error "Database backup integrity check failed!"
        exit 1
    fi
fi

# Display backup summary
BACKUP_SIZE=$(du -sh "$BACKUP_DIR/stash_filter_$TIMESTAMP.db" | cut -f1)
TOTAL_BACKUPS=$(ls -1 "$BACKUP_DIR"/stash_filter_*.db 2>/dev/null | wc -l)

log "Backup completed successfully!"
log "Backup size: $BACKUP_SIZE"
log "Total backups retained: $TOTAL_BACKUPS"

# Optional: Upload to cloud storage
if [ -n "$CLOUD_BACKUP_SCRIPT" ] && [ -f "$CLOUD_BACKUP_SCRIPT" ]; then
    log "Running cloud backup script..."
    "$CLOUD_BACKUP_SCRIPT" "$BACKUP_DIR/stash_filter_$TIMESTAMP.db"
fi

log "Backup process finished."
