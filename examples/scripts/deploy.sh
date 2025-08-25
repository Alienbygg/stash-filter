#!/bin/bash
# Stash-Filter Quick Deployment Script
# Automated setup for new installations

set -e

# Configuration
REPO_URL="https://github.com/your-username/stash-filter.git"
INSTALL_DIR="${INSTALL_DIR:-stash-filter}"
COMPOSE_FILE="docker-compose.yml"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')] $1${NC}"
}

header() {
    echo
    echo -e "${BOLD}${GREEN}$1${NC}"
    echo -e "${GREEN}$(echo "$1" | sed 's/./=/g')${NC}"
}

# Check system requirements
check_requirements() {
    header "Checking System Requirements"
    
    # Check Docker
    if ! command -v docker >/dev/null 2>&1; then
        error "Docker is not installed. Please install Docker first."
        error "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    log "Docker found: $(docker --version)"
    
    # Check Docker Compose
    if ! command -v docker-compose >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1; then
        error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    if command -v docker-compose >/dev/null 2>&1; then
        log "Docker Compose found: $(docker-compose --version)"
    else
        log "Docker Compose found: $(docker compose version)"
    fi
    
    # Check Git
    if ! command -v git >/dev/null 2>&1; then
        warn "Git is not installed. Will download archive instead."
    else
        log "Git found: $(git --version)"
    fi
    
    # Check available disk space
    local available_space=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$available_space" -lt 2 ]; then
        warn "Less than 2GB disk space available. Consider freeing up space."
    else
        log "Available disk space: ${available_space}GB"
    fi
}

# Download project files
download_project() {
    header "Downloading Stash-Filter"
    
    if [ -d "$INSTALL_DIR" ]; then
        warn "Directory $INSTALL_DIR already exists"
        read -p "Do you want to remove it and continue? (y/N): " -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$INSTALL_DIR"
            log "Removed existing directory"
        else
            error "Installation cancelled"
            exit 1
        fi
    fi
    
    if command -v git >/dev/null 2>&1; then
        log "Cloning repository..."
        git clone "$REPO_URL" "$INSTALL_DIR"
        cd "$INSTALL_DIR"
    else
        log "Downloading archive..."
        curl -L -o stash-filter.zip "https://github.com/your-username/stash-filter/archive/main.zip"
        unzip stash-filter.zip
        mv stash-filter-main "$INSTALL_DIR"
        rm stash-filter.zip
        cd "$INSTALL_DIR"
    fi
    
    log "Project downloaded to $INSTALL_DIR"
}

# Generate secure secrets
generate_secrets() {
    header "Generating Secure Configuration"
    
    # Generate secret key
    local secret_key
    if command -v python3 >/dev/null 2>&1; then
        secret_key=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    elif command -v openssl >/dev/null 2>&1; then
        secret_key=$(openssl rand -hex 32)
    else
        secret_key="change-this-insecure-default-$(date +%s)"
        warn "Could not generate secure key. Using timestamp-based key."
    fi
    
    log "Generated secure secret key"
    echo "$secret_key"
}

# Interactive configuration
configure_environment() {
    header "Configuration Setup"
    
    local secret_key
    secret_key=$(generate_secrets)
    
    log "Creating environment configuration..."
    
    # Get Stash information
    echo
    info "Stash Configuration:"
    read -p "Enter your Stash server URL (e.g., http://192.168.1.100:9999): " stash_url
    read -p "Enter your Stash API key: " stash_api_key
    
    # Optional Whisparr configuration
    echo
    info "Whisparr Configuration (optional - press Enter to skip):"
    read -p "Enter your Whisparr server URL: " whisparr_url
    if [ -n "$whisparr_url" ]; then
        read -p "Enter your Whisparr API key: " whisparr_api_key
    fi
    
    # Optional StashDB configuration
    echo
    info "StashDB Configuration (optional - press Enter to skip):"
    read -p "Enter your StashDB API key: " stashdb_api_key
    
    # Create .env file
    cat > .env << EOF
# Stash-Filter Environment Configuration
# Generated on $(date)

# Required - Stash server configuration
STASH_URL=$stash_url
STASH_API_KEY=$stash_api_key

# Required - Application security
SECRET_KEY=$secret_key

# Application settings
LOG_LEVEL=INFO
FLASK_ENV=production
DATABASE_PATH=/app/data/stash_filter.db

# Discovery settings
DISCOVERY_FREQUENCY_HOURS=24
MAX_SCENES_PER_CHECK=100

# Optional - Whisparr integration
WHISPARR_URL=$whisparr_url
WHISPARR_API_KEY=$whisparr_api_key

# Optional - StashDB integration
STASHDB_URL=https://stashdb.org
STASHDB_API_KEY=$stashdb_api_key

# Performance settings
CONCURRENT_REQUESTS=3
REQUEST_TIMEOUT=30
EOF
    
    log "Environment configuration created"
}

# Setup directories
setup_directories() {
    header "Setting Up Directories"
    
    local dirs=("data" "logs" "config" "backups")
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
        log "Created directory: $dir"
    done
    
    # Set proper permissions
    chmod 755 data logs config backups
    log "Set directory permissions"
}

# Test configuration
test_configuration() {
    header "Testing Configuration"
    
    log "Validating environment configuration..."
    
    # Source the environment
    source .env
    
    # Basic validation
    if [ -z "$STASH_URL" ] || [ -z "$STASH_API_KEY" ]; then
        error "Missing required Stash configuration"
        return 1
    fi
    
    # Test Stash connectivity
    log "Testing Stash connectivity..."
    if command -v curl >/dev/null 2>&1; then
        local stash_test=$(echo "$STASH_URL" | sed 's|/$||')/graphql
        if curl -f -s -m 10 "$stash_test" -H "Content-Type: application/json" -d '{"query":"query { version }"}' >/dev/null 2>&1; then
            log "✓ Stash connection successful"
        else
            warn "✗ Could not connect to Stash. Please verify URL and network connectivity."
        fi
    else
        warn "curl not available, skipping connectivity test"
    fi
    
    log "Configuration validation completed"
}

# Deploy application
deploy_application() {
    header "Deploying Application"
    
    # Choose compose command
    local compose_cmd="docker-compose"
    if ! command -v docker-compose >/dev/null 2>&1; then
        compose_cmd="docker compose"
    fi
    
    log "Pulling Docker images..."
    $compose_cmd pull
    
    log "Starting Stash-Filter..."
    $compose_cmd up -d
    
    log "Waiting for application to start..."
    local max_wait=60
    local wait_time=0
    
    while [ $wait_time -lt $max_wait ]; do
        if curl -f -s http://localhost:5000/health >/dev/null 2>&1; then
            log "✓ Application is running and healthy"
            break
        fi
        sleep 2
        wait_time=$((wait_time + 2))
        echo -n "."
    done
    
    if [ $wait_time -ge $max_wait ]; then
        warn "Application may not have started properly"
        warn "Check logs with: $compose_cmd logs stash-filter"
    fi
}

# Setup cron jobs
setup_maintenance() {
    header "Setting Up Maintenance"
    
    # Make scripts executable
    if [ -d "examples/scripts" ]; then
        chmod +x examples/scripts/*.sh
        log "Made maintenance scripts executable"
        
        # Ask about cron setup
        read -p "Do you want to set up automatic maintenance? (y/N): " -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            info "Add these lines to your crontab (run 'crontab -e'):"
            echo
            echo "# Stash-Filter maintenance"
            echo "0 2 * * 0 $(pwd)/examples/scripts/maintenance.sh"
            echo "*/15 * * * * $(pwd)/examples/scripts/health-check.sh"
            echo "0 3 * * * $(pwd)/examples/scripts/backup.sh"
            echo
        fi
    fi
}

# Post-installation instructions
show_completion() {
    header "Installation Complete!"
    
    log "Stash-Filter has been successfully deployed"
    
    echo
    info "Next Steps:"
    echo "1. Open your browser and go to: http://localhost:5000"
    echo "2. Configure your filtering preferences in Settings"
    echo "3. Sync your favorites from Stash"
    echo "4. Enable monitoring for performers/studios you want to track"
    echo "5. Run your first discovery to test the setup"
    
    echo
    info "Useful Commands:"
    echo "- View logs: docker-compose logs -f stash-filter"
    echo "- Stop service: docker-compose down"
    echo "- Update: docker-compose pull && docker-compose up -d"
    echo "- Backup: ./examples/scripts/backup.sh"
    
    echo
    info "Documentation:"
    echo "- User Guide: docs/user-guide.md"
    echo "- Troubleshooting: docs/faq.md"
    echo "- API Documentation: API.md"
    
    if [ -f ".env" ]; then
        echo
        warn "Security Note:"
        warn "Your .env file contains sensitive API keys"
        warn "Never commit this file to version control"
        warn "Keep backups of your configuration in a secure location"
    fi
}

# Cleanup on exit
cleanup() {
    if [ $? -ne 0 ]; then
        error "Installation failed"
        warn "Check the error messages above and try again"
        warn "You can also run this script with --help for more options"
    fi
}

# Show usage
show_usage() {
    echo "Stash-Filter Quick Deployment Script"
    echo
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  --help              Show this help message"
    echo "  --unattended        Run in unattended mode (requires environment variables)"
    echo "  --install-dir DIR   Specify installation directory (default: stash-filter)"
    echo "  --skip-tests        Skip configuration testing"
    echo "  --skip-deploy       Skip Docker deployment (setup only)"
    echo
    echo "Environment Variables for Unattended Mode:"
    echo "  STASH_URL          Stash server URL"
    echo "  STASH_API_KEY      Stash API key"  
    echo "  WHISPARR_URL       Whisparr server URL (optional)"
    echo "  WHISPARR_API_KEY   Whisparr API key (optional)"
    echo "  STASHDB_API_KEY    StashDB API key (optional)"
    echo
    echo "Example:"
    echo "  STASH_URL=http://192.168.1.100:9999 STASH_API_KEY=your-key $0 --unattended"
}

# Parse command line arguments
UNATTENDED=false
SKIP_TESTS=false
SKIP_DEPLOY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            show_usage
            exit 0
            ;;
        --unattended)
            UNATTENDED=true
            shift
            ;;
        --install-dir)
            INSTALL_DIR="$2"
            shift 2
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-deploy)
            SKIP_DEPLOY=true
            shift
            ;;
        *)
            error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main installation process
main() {
    trap cleanup EXIT
    
    header "Stash-Filter Quick Deployment"
    info "This script will help you set up Stash-Filter quickly"
    
    # System checks
    check_requirements
    
    # Download project
    download_project
    
    # Configuration
    if [ "$UNATTENDED" = true ]; then
        if [ -z "$STASH_URL" ] || [ -z "$STASH_API_KEY" ]; then
            error "Unattended mode requires STASH_URL and STASH_API_KEY environment variables"
            exit 1
        fi
        
        log "Running in unattended mode"
        local secret_key
        secret_key=$(generate_secrets)
        
        cat > .env << EOF
STASH_URL=$STASH_URL
STASH_API_KEY=$STASH_API_KEY
SECRET_KEY=$secret_key
WHISPARR_URL=${WHISPARR_URL:-}
WHISPARR_API_KEY=${WHISPARR_API_KEY:-}
STASHDB_API_KEY=${STASHDB_API_KEY:-}
LOG_LEVEL=INFO
FLASK_ENV=production
EOF
        log "Configuration created from environment variables"
    else
        configure_environment
    fi
    
    # Setup directories
    setup_directories
    
    # Test configuration
    if [ "$SKIP_TESTS" != true ]; then
        test_configuration
    fi
    
    # Deploy application
    if [ "$SKIP_DEPLOY" != true ]; then
        deploy_application
    fi
    
    # Setup maintenance
    setup_maintenance
    
    # Show completion message
    show_completion
}

# Run main function if script is executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
