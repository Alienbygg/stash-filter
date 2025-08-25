#!/bin/bash
# Stash-Filter Maintenance Script
# Performs database optimization and cleanup tasks

set -e

# Configuration
DATA_DIR="${DATA_DIR:-./data}"
DB_FILE="$DATA_DIR/stash_filter.db"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
VACUUM_THRESHOLD="${VACUUM_THRESHOLD:-10}"  # MB of unused space
LOG_RETENTION_DAYS="${LOG_RETENTION_DAYS:-30}"
DISCOVERY_LOG_RETENTION_DAYS="${DISCOVERY_LOG_RETENTION_DAYS:-90}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Check if database exists
check_database() {
    if [ ! -f "$DB_FILE" ]; then
        error "Database file not found: $DB_FILE"
        exit 1
    fi
    
    if ! command -v sqlite3 >/dev/null 2>&1; then
        error "sqlite3 command not found. Please install sqlite3."
        exit 1
    fi
    
    log "Database found: $DB_FILE"
}

# Create backup before maintenance
create_backup() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/maintenance_backup_$timestamp.db"
    
    log "Creating maintenance backup..."
    mkdir -p "$BACKUP_DIR"
    
    sqlite3 "$DB_FILE" ".backup $backup_file"
    log "Backup created: $backup_file"
}

# Check database integrity
check_integrity() {
    log "Checking database integrity..."
    
    local result=$(sqlite3 "$DB_FILE" "PRAGMA integrity_check;")
    
    if [ "$result" = "ok" ]; then
        log "Database integrity check passed"
    else
        error "Database integrity check failed: $result"
        exit 1
    fi
}

# Get database statistics
get_db_stats() {
    log "Getting database statistics..."
    
    # Database size
    local db_size=$(ls -lh "$DB_FILE" | awk '{print $5}')
    info "Database size: $db_size"
    
    # Page count and free pages
    local page_count=$(sqlite3 "$DB_FILE" "PRAGMA page_count;")
    local freelist_count=$(sqlite3 "$DB_FILE" "PRAGMA freelist_count;")
    local page_size=$(sqlite3 "$DB_FILE" "PRAGMA page_size;")
    
    local total_size=$((page_count * page_size))
    local free_size=$((freelist_count * page_size))
    local free_mb=$((free_size / 1024 / 1024))
    
    info "Total pages: $page_count"
    info "Free pages: $freelist_count"
    info "Free space: ${free_mb}MB"
    
    # Table row counts
    local performers=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM performers;" 2>/dev/null || echo "0")
    local studios=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM studios;" 2>/dev/null || echo "0")
    local scenes=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM scenes;" 2>/dev/null || echo "0")
    local wanted_scenes=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM wanted_scenes;" 2>/dev/null || echo "0")
    
    info "Performers: $performers"
    info "Studios: $studios" 
    info "Scenes: $scenes"
    info "Wanted scenes: $wanted_scenes"
    
    echo "$free_mb"  # Return free space for vacuum decision
}

# Vacuum database if needed
vacuum_database() {
    local free_mb="$1"
    
    if [ "$free_mb" -gt "$VACUUM_THRESHOLD" ]; then
        log "Vacuuming database (${free_mb}MB free space)..."
        
        local before_size=$(stat -f%z "$DB_FILE" 2>/dev/null || stat -c%s "$DB_FILE")
        
        sqlite3 "$DB_FILE" "VACUUM;"
        
        local after_size=$(stat -f%z "$DB_FILE" 2>/dev/null || stat -c%s "$DB_FILE")
        local saved_mb=$(((before_size - after_size) / 1024 / 1024))
        
        log "Vacuum completed. Space saved: ${saved_mb}MB"
    else
        info "Vacuum not needed (only ${free_mb}MB free space)"
    fi
}

# Analyze database for query optimization
analyze_database() {
    log "Analyzing database for query optimization..."
    sqlite3 "$DB_FILE" "ANALYZE;"
    log "Database analysis completed"
}

# Clean up old discovery logs
cleanup_discovery_logs() {
    log "Cleaning up old discovery logs..."
    
    # This would depend on your actual schema
    # Example cleanup queries:
    local deleted=$(sqlite3 "$DB_FILE" "
        DELETE FROM discovery_logs 
        WHERE created_date < datetime('now', '-$DISCOVERY_LOG_RETENTION_DAYS days');
        SELECT changes();
    " 2>/dev/null || echo "0")
    
    if [ "$deleted" -gt 0 ]; then
        log "Deleted $deleted old discovery log entries"
    else
        info "No old discovery logs to clean up"
    fi
}

# Clean up orphaned records
cleanup_orphaned_records() {
    log "Cleaning up orphaned records..."
    
    # Clean up scenes without performers or studios
    local orphaned_scenes=$(sqlite3 "$DB_FILE" "
        DELETE FROM scenes 
        WHERE performer_id IS NOT NULL 
        AND performer_id NOT IN (SELECT id FROM performers)
        OR studio_id IS NOT NULL 
        AND studio_id NOT IN (SELECT id FROM studios);
        SELECT changes();
    " 2>/dev/null || echo "0")
    
    # Clean up wanted scenes for deleted scenes
    local orphaned_wanted=$(sqlite3 "$DB_FILE" "
        DELETE FROM wanted_scenes 
        WHERE scene_id NOT IN (SELECT id FROM scenes);
        SELECT changes();
    " 2>/dev/null || echo "0")
    
    if [ "$orphaned_scenes" -gt 0 ] || [ "$orphaned_wanted" -gt 0 ]; then
        log "Cleaned up $orphaned_scenes orphaned scenes and $orphaned_wanted orphaned wanted scenes"
    else
        info "No orphaned records found"
    fi
}

# Update statistics
update_statistics() {
    log "Updating database statistics..."
    
    # Update performer scene counts
    sqlite3 "$DB_FILE" "
        UPDATE performers 
        SET scene_count = (
            SELECT COUNT(*) 
            FROM scenes 
            WHERE performer_id = performers.id
        );
    " 2>/dev/null || warn "Could not update performer statistics"
    
    # Update studio scene counts  
    sqlite3 "$DB_FILE" "
        UPDATE studios 
        SET scene_count = (
            SELECT COUNT(*) 
            FROM scenes 
            WHERE studio_id = studios.id
        );
    " 2>/dev/null || warn "Could not update studio statistics"
    
    log "Statistics updated"
}

# Clean up application logs
cleanup_app_logs() {
    log "Cleaning up application logs..."
    
    local log_dir="./logs"
    if [ -d "$log_dir" ]; then
        # Remove logs older than retention period
        find "$log_dir" -name "*.log" -mtime +$LOG_RETENTION_DAYS -delete 2>/dev/null || true
        find "$log_dir" -name "*.log.*" -mtime +$LOG_RETENTION_DAYS -delete 2>/dev/null || true
        
        # Compress large current log files
        find "$log_dir" -name "*.log" -size +10M -exec gzip {} \; 2>/dev/null || true
        
        log "Application logs cleaned up"
    fi
}

# Generate maintenance report
generate_report() {
    log "Generating maintenance report..."
    
    local report_file="maintenance_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "Stash-Filter Maintenance Report"
        echo "Date: $(date)"
        echo "================================"
        echo
        
        echo "Database Information:"
        echo "- File: $DB_FILE"
        echo "- Size: $(ls -lh "$DB_FILE" | awk '{print $5}')"
        
        echo
        echo "Table Counts:"
        sqlite3 "$DB_FILE" "
            SELECT 'Performers: ' || COUNT(*) FROM performers
            UNION ALL
            SELECT 'Studios: ' || COUNT(*) FROM studios
            UNION ALL  
            SELECT 'Scenes: ' || COUNT(*) FROM scenes
            UNION ALL
            SELECT 'Wanted Scenes: ' || COUNT(*) FROM wanted_scenes;
        " 2>/dev/null || echo "Could not get table counts"
        
        echo
        echo "Recent Activity:"
        sqlite3 "$DB_FILE" "
            SELECT 'Last Discovery: ' || MAX(created_date) FROM scenes
            UNION ALL
            SELECT 'Newest Scene: ' || MAX(release_date) FROM scenes  
            UNION ALL
            SELECT 'Wanted Scenes Added Today: ' || COUNT(*) 
            FROM wanted_scenes 
            WHERE date(added_date) = date('now');
        " 2>/dev/null || echo "Could not get activity information"
        
    } > "$report_file"
    
    log "Maintenance report saved: $report_file"
}

# Main maintenance function
main() {
    log "Starting Stash-Filter maintenance..."
    
    # Pre-maintenance checks
    check_database
    check_integrity
    
    # Create backup
    create_backup
    
    # Get current stats and determine if vacuum is needed
    local free_mb
    free_mb=$(get_db_stats)
    
    # Perform cleanup operations
    cleanup_discovery_logs
    cleanup_orphaned_records
    update_statistics
    
    # Optimize database
    vacuum_database "$free_mb"
    analyze_database
    
    # Clean up logs
    cleanup_app_logs
    
    # Final integrity check
    check_integrity
    
    # Generate report
    generate_report
    
    # Final stats
    log "Final database statistics:"
    get_db_stats >/dev/null
    
    log "Maintenance completed successfully!"
}

# Show usage information
show_usage() {
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  --help              Show this help message"
    echo "  --check-only        Only check database integrity, don't perform maintenance"
    echo "  --vacuum-only       Only vacuum the database"
    echo "  --stats-only        Only show database statistics"
    echo "  --backup-only       Only create a backup"
    echo
    echo "Environment Variables:"
    echo "  DATA_DIR            Path to data directory (default: ./data)"
    echo "  BACKUP_DIR          Path to backup directory (default: ./backups)"
    echo "  VACUUM_THRESHOLD    MB of free space to trigger vacuum (default: 10)"
    echo "  LOG_RETENTION_DAYS  Days to keep application logs (default: 30)"
}

# Handle command line arguments
case "${1:-}" in
    --help)
        show_usage
        exit 0
        ;;
    --check-only)
        check_database
        check_integrity
        log "Database integrity check completed"
        ;;
    --vacuum-only)
        check_database
        create_backup
        local free_mb
        free_mb=$(get_db_stats)
        vacuum_database "$free_mb"
        ;;
    --stats-only)
        check_database
        get_db_stats >/dev/null
        ;;
    --backup-only)
        check_database
        create_backup
        ;;
    "")
        main
        ;;
    *)
        error "Unknown option: $1"
        show_usage
        exit 1
        ;;
esac
