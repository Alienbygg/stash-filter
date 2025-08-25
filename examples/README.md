# Examples Directory

This directory contains comprehensive examples and templates for various Stash-Filter deployment scenarios and configurations.

## 📁 Directory Structure

```
examples/
├── configurations/         # Environment configuration examples
├── docker-compose/        # Docker Compose deployment examples
└── scripts/               # Utility and maintenance scripts
```

## 🔧 Configuration Examples

### [`configurations/`](configurations/)

Ready-to-use environment configuration files for different deployment scenarios:

#### [`basic.env`](configurations/basic.env)
- Minimal setup for getting started
- Required environment variables only
- Perfect for first-time installation

#### [`advanced.env`](configurations/advanced.env)
- Full-featured setup with all integrations
- Whisparr and StashDB integration
- Performance tuning options
- Advanced configuration settings

#### [`development.env`](configurations/development.env)
- Local development environment
- Debug settings enabled
- Fast iteration configuration
- Development-specific optimizations

#### [`production.env`](configurations/production.env)
- Security-focused production setup
- Conservative discovery settings
- Enhanced monitoring and logging
- Production-grade security options

### Usage
1. Choose the configuration that matches your needs
2. Copy to `.env` in your project root:
   ```bash
   cp examples/configurations/basic.env .env
   ```
3. Edit the values to match your environment
4. Never commit the `.env` file to version control!

## 🐳 Docker Compose Examples

### [`docker-compose/`](docker-compose/)

Complete Docker Compose configurations for different deployment scenarios:

#### [`simple.yml`](docker-compose/simple.yml)
- **Use Case**: Basic single-container deployment
- **Features**: Stash-Filter only, minimal configuration
- **Best For**: Testing, small setups, single-user deployments

#### [`full-stack.yml`](docker-compose/full-stack.yml)
- **Use Case**: Complete media stack deployment  
- **Features**: Stash + Whisparr + Stash-Filter + Traefik reverse proxy
- **Best For**: Home media servers, comprehensive setups
- **Includes**: SSL termination, domain routing, database browser

#### [`production.yml`](docker-compose/production.yml)
- **Use Case**: Production deployment with monitoring
- **Features**: Security hardening, monitoring stack, backup system
- **Best For**: Production environments, enterprise deployments
- **Includes**: Prometheus, Grafana, Loki, automated backups

### Usage
1. Choose the appropriate compose file
2. Copy to your project root:
   ```bash
   cp examples/docker-compose/simple.yml docker-compose.yml
   ```
3. Customize service configurations as needed
4. Deploy with `docker-compose up -d`

## 📜 Utility Scripts

### [`scripts/`](scripts/)

Professional-grade maintenance and deployment scripts:

#### [`backup.sh`](scripts/backup.sh)
- **Purpose**: Automated database and configuration backup
- **Features**: 
  - SQLite database backup with integrity verification
  - Configuration file backup (sanitized)
  - Automatic cleanup of old backups
  - Cloud backup integration support
- **Usage**: 
  ```bash
  ./examples/scripts/backup.sh
  # or set up as cron job: 0 2 * * * /path/to/backup.sh
  ```

#### [`health-check.sh`](scripts/health-check.sh)
- **Purpose**: Comprehensive health monitoring and alerting
- **Features**:
  - HTTP endpoint monitoring
  - Docker container health checking
  - Database connectivity verification
  - Disk space and memory monitoring
  - Discord/Slack/Email notifications
- **Usage**:
  ```bash
  # Manual check
  ./examples/scripts/health-check.sh
  
  # Continuous monitoring (cron)
  */15 * * * * /path/to/health-check.sh
  ```

#### [`maintenance.sh`](scripts/maintenance.sh)
- **Purpose**: Database optimization and system cleanup
- **Features**:
  - Database vacuuming and analysis
  - Orphaned record cleanup
  - Log rotation and cleanup
  - Statistics updates
  - Performance optimization
- **Usage**:
  ```bash
  # Full maintenance
  ./examples/scripts/maintenance.sh
  
  # Specific operations
  ./examples/scripts/maintenance.sh --vacuum-only
  ./examples/scripts/maintenance.sh --stats-only
  ```

#### [`deploy.sh`](scripts/deploy.sh)
- **Purpose**: Automated deployment and setup
- **Features**:
  - Interactive and unattended installation modes
  - Dependency checking and validation
  - Configuration generation
  - Connection testing
  - Post-installation setup
- **Usage**:
  ```bash
  # Interactive installation
  curl -sSL https://raw.githubusercontent.com/your-username/stash-filter/main/examples/scripts/deploy.sh | bash
  
  # Unattended installation
  STASH_URL=http://192.168.1.100:9999 STASH_API_KEY=your-key ./deploy.sh --unattended
  ```

### Script Features

**Common Features Across All Scripts:**
- ✅ Comprehensive error handling
- ✅ Detailed logging with timestamps
- ✅ Color-coded output for better readability
- ✅ Help documentation and usage examples
- ✅ Environment variable configuration
- ✅ Dry-run and testing modes where applicable

**Security Considerations:**
- 🔒 No hardcoded credentials or sensitive data
- 🔒 Sanitized backup exports (API keys removed)
- 🔒 Secure file permissions checking
- 🔒 Input validation and error handling

## 📋 Quick Start Examples

### 1. Basic Setup
```bash
# Clone repository
git clone https://github.com/your-username/stash-filter.git
cd stash-filter

# Use basic configuration
cp examples/configurations/basic.env .env
nano .env  # Edit your Stash URL and API key

# Use simple Docker Compose
cp examples/docker-compose/simple.yml docker-compose.yml

# Deploy
docker-compose up -d
```

### 2. Full Stack Setup
```bash
# Use advanced configuration
cp examples/configurations/advanced.env .env
nano .env  # Configure all your services

# Use full stack compose
cp examples/docker-compose/full-stack.yml docker-compose.yml

# Create required directories
mkdir -p traefik/dynamic certs

# Deploy full stack
docker-compose up -d
```

### 3. Production Deployment
```bash
# Use production configuration
cp examples/configurations/production.env .env

# Use production compose with monitoring
cp examples/docker-compose/production.yml docker-compose.yml

# Set up monitoring configs
mkdir -p monitoring/{prometheus,grafana,loki}

# Make scripts executable
chmod +x examples/scripts/*.sh

# Deploy with monitoring
docker-compose up -d
```

## 🔧 Customization Tips

### Environment Variables
- **Always change default secrets** in production
- **Use strong, unique passwords** for all services
- **Configure proper network access** (localhost vs 0.0.0.0)
- **Set appropriate resource limits** based on your hardware

### Docker Compose Modifications
- **Adjust port mappings** to avoid conflicts
- **Configure volume mounts** for your directory structure  
- **Set resource limits** based on available hardware
- **Enable/disable services** as needed for your setup

### Script Customization
- **Set environment variables** for your specific paths
- **Adjust retention periods** for backups and logs
- **Configure notification endpoints** (webhooks, email)
- **Modify scheduling** in cron jobs as needed

## 🛡️ Security Best Practices

### Configuration Security
```bash
# Generate secure secret keys
python3 -c "import secrets; print(secrets.token_hex(32))"

# Set proper file permissions
chmod 600 .env
chmod 700 data/ logs/

# Never commit sensitive files
echo ".env" >> .gitignore
echo "*.env" >> .gitignore
```

### Network Security
```yaml
# Restrict network access in docker-compose.yml
ports:
  - "127.0.0.1:5000:5000"  # Localhost only

# Use internal networks
networks:
  internal:
    internal: true
```

### Backup Security
```bash
# Encrypt sensitive backups
gpg --symmetric --cipher-algo AES256 backup.db

# Secure backup storage
rsync -avz --delete backups/ user@backup-server:/secure/path/
```

## 📞 Support and Troubleshooting

### Common Issues

**Configuration Problems:**
- Check file permissions (`chmod 600 .env`)
- Verify all required variables are set
- Test API connectivity manually

**Docker Issues:**
- Check port conflicts (`netstat -tlnp | grep :5000`)
- Verify Docker networks (`docker network ls`)
- Review container logs (`docker-compose logs stash-filter`)

**Script Issues:**
- Ensure scripts are executable (`chmod +x script.sh`)
- Check script dependencies (sqlite3, curl, etc.)
- Run with debug output for troubleshooting

### Getting Help

1. **Check the logs** first - most issues are logged
2. **Review the documentation** in the main `docs/` directory
3. **Search existing issues** on GitHub
4. **Create a new issue** with:
   - Your configuration (sanitized)
   - Relevant log output
   - Steps to reproduce
   - Expected vs actual behavior

### Contributing Examples

Have a useful configuration or script? Contributions welcome!

1. **Test thoroughly** in your environment
2. **Remove sensitive data** (IPs, keys, personal info)
3. **Add documentation** explaining the use case
4. **Follow the existing structure** and naming conventions
5. **Submit a pull request** with clear description

---

*These examples are maintained by the community and updated regularly. Always review and test configurations before deploying to production!*
