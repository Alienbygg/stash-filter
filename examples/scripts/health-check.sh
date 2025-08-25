#!/bin/bash
# Stash-Filter Health Monitoring Script
# Monitors application health and sends alerts

set -e

# Configuration
STASH_FILTER_URL="${STASH_FILTER_URL:-http://localhost:5000}"
CONTAINER_NAME="${CONTAINER_NAME:-stash-filter}"
ALERT_EMAIL="${ALERT_EMAIL:-}"
DISCORD_WEBHOOK="${DISCORD_WEBHOOK:-}"
SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"
LOG_FILE="${LOG_FILE:-./monitoring.log}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Status tracking
STATUS_FILE="/tmp/stash_filter_status.txt"
LAST_STATUS=$(cat "$STATUS_FILE" 2>/dev/null || echo "unknown")

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1" >> "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1" >> "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Send notification function
send_notification() {
    local status="$1"
    local message="$2"
    local color="$3"
    
    # Discord notification
    if [ -n "$DISCORD_WEBHOOK" ]; then
        curl -s -X POST "$DISCORD_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{
                \"embeds\": [{
                    \"title\": \"Stash-Filter $status\",
                    \"description\": \"$message\",
                    \"color\": $color,
                    \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)\",
                    \"fields\": [{
                        \"name\": \"Server\",
                        \"value\": \"$(hostname)\",
                        \"inline\": true
                    }]
                }]
            }" >/dev/null 2>&1
    fi
    
    # Slack notification
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -s -X POST "$SLACK_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{
                \"text\": \"Stash-Filter $status: $message\",
                \"username\": \"Stash-Filter Monitor\",
                \"icon_emoji\": \":warning:\"
            }" >/dev/null 2>&1
    fi
    
    # Email notification
    if [ -n "$ALERT_EMAIL" ] && command -v mail >/dev/null 2>&1; then
        echo "$message" | mail -s "Stash-Filter $status Alert" "$ALERT_EMAIL"
    fi
}

# Check HTTP health endpoint
check_http_health() {
    local response
    local http_code
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$STASH_FILTER_URL/health" --max-time 10 2>/dev/null)
    http_code=$(echo "$response" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    
    if [ "$http_code" = "200" ]; then
        local body=$(echo "$response" | sed -e 's/HTTPSTATUS:.*//g')
        if echo "$body" | grep -q '"status": "healthy"'; then
            return 0
        fi
    fi
    return 1
}

# Check Docker container status
check_container_status() {
    if ! command -v docker >/dev/null 2>&1; then
        return 0  # Skip if Docker not available
    fi
    
    if ! docker ps --format "table {{.Names}}" | grep -q "^$CONTAINER_NAME$"; then
        return 1
    fi
    
    # Check if container is healthy
    local health_status=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "none")
    if [ "$health_status" = "healthy" ] || [ "$health_status" = "none" ]; then
        return 0
    fi
    return 1
}

# Check database health
check_database_health() {
    local db_path="./data/stash_filter.db"
    
    if [ ! -f "$db_path" ]; then
        return 1
    fi
    
    if command -v sqlite3 >/dev/null 2>&1; then
        if ! sqlite3 "$db_path" "SELECT 1;" >/dev/null 2>&1; then
            return 1
        fi
    fi
    
    return 0
}

# Check disk space
check_disk_space() {
    local usage=$(df . | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$usage" -gt 90 ]; then
        return 1
    fi
    return 0
}

# Check memory usage
check_memory_usage() {
    if ! command -v docker >/dev/null 2>&1; then
        return 0  # Skip if Docker not available
    fi
    
    local memory_usage=$(docker stats --no-stream --format "table {{.Container}}\t{{.MemPerc}}" | grep "$CONTAINER_NAME" | awk '{print $2}' | sed 's/%//' 2>/dev/null || echo "0")
    
    if [ "${memory_usage%.*}" -gt 90 ] 2>/dev/null; then
        return 1
    fi
    return 0
}

# Get system metrics
get_system_metrics() {
    local cpu_usage=""
    local memory_usage=""
    local disk_usage=""
    
    if command -v docker >/dev/null 2>&1; then
        local stats=$(docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemPerc}}" | grep "$CONTAINER_NAME" 2>/dev/null || echo "")
        if [ -n "$stats" ]; then
            cpu_usage=$(echo "$stats" | awk '{print $2}')
            memory_usage=$(echo "$stats" | awk '{print $3}')
        fi
    fi
    
    disk_usage=$(df . | awk 'NR==2 {print $5}')
    
    info "System Metrics - CPU: ${cpu_usage:-N/A}, Memory: ${memory_usage:-N/A}, Disk: $disk_usage"
}

# Main health check
main() {
    log "Starting health check for Stash-Filter..."
    
    local current_status="healthy"
    local issues=()
    
    # HTTP Health Check
    if ! check_http_health; then
        current_status="unhealthy"
        issues+=("HTTP health check failed")
        error "HTTP health check failed"
    else
        log "HTTP health check passed"
    fi
    
    # Container Status Check
    if ! check_container_status; then
        current_status="unhealthy" 
        issues+=("Container is not running or unhealthy")
        error "Container status check failed"
    else
        log "Container status check passed"
    fi
    
    # Database Health Check
    if ! check_database_health; then
        current_status="degraded"
        issues+=("Database health check failed")
        warn "Database health check failed"
    else
        log "Database health check passed"
    fi
    
    # Disk Space Check
    if ! check_disk_space; then
        current_status="warning"
        issues+=("Disk space usage > 90%")
        warn "Disk space usage is high"
    else
        log "Disk space check passed"
    fi
    
    # Memory Usage Check
    if ! check_memory_usage; then
        current_status="warning"
        issues+=("Memory usage > 90%")
        warn "Memory usage is high"
    else
        log "Memory usage check passed"
    fi
    
    # Get system metrics
    get_system_metrics
    
    # Status change detection and notification
    if [ "$current_status" != "$LAST_STATUS" ]; then
        log "Status changed from $LAST_STATUS to $current_status"
        
        case "$current_status" in
            "healthy")
                send_notification "RECOVERED" "Stash-Filter has recovered and is now healthy" "65280"  # Green
                ;;
            "warning")
                send_notification "WARNING" "Stash-Filter has warnings: $(IFS=', '; echo "${issues[*]}")" "16776960"  # Yellow
                ;;
            "degraded")
                send_notification "DEGRADED" "Stash-Filter is degraded: $(IFS=', '; echo "${issues[*]}")" "16744448"  # Orange
                ;;
            "unhealthy")
                send_notification "CRITICAL" "Stash-Filter is unhealthy: $(IFS=', '; echo "${issues[*]}")" "16711680"  # Red
                ;;
        esac
        
        echo "$current_status" > "$STATUS_FILE"
    fi
    
    log "Health check completed - Status: $current_status"
    
    # Exit with appropriate code
    case "$current_status" in
        "healthy") exit 0 ;;
        "warning") exit 1 ;;
        "degraded") exit 2 ;;
        "unhealthy") exit 3 ;;
    esac
}

# Script execution
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
