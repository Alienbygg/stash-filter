# Installation Guide

This guide covers various ways to install and configure Stash-Filter.

## Prerequisites

### System Requirements
- **CPU**: 1 CPU core minimum, 2+ cores recommended
- **RAM**: 512MB minimum, 1GB+ recommended for large libraries
- **Storage**: 100MB for application, additional space for database growth
- **Network**: Access to Stash server and internet for StashDB/Whisparr

### Required Services
- **Stash**: Version 0.20.0 or newer
- **Docker**: Version 20.10 or newer
- **Docker Compose**: Version 2.0 or newer (optional but recommended)

### Optional Services
- **Whisparr**: For automatic downloads
- **StashDB Account**: For enhanced scene discovery
- **Reverse Proxy**: nginx, Traefik, or Caddy for SSL/domain access

## Installation Methods

### Method 1: Docker Compose (Recommended)

This is the easiest and most reliable installation method.

1. **Create project directory:**
```bash
mkdir stash-filter
cd stash-filter
```

2. **Download configuration files:**
```bash
# Download docker-compose.yml
curl -O https://raw.githubusercontent.com/your-username/stash-filter/main/docker-compose.yml

# Download environment template
curl -O https://raw.githubusercontent.com/your-username/stash-filter/main/.env.example
cp .env.example .env
```

3. **Configure environment variables:**
```bash
nano .env
```

Edit the following required variables:
```env
# Required - Your Stash server details
STASH_URL=http://192.168.1.100:9999
STASH_API_KEY=your-stash-api-key-here

# Required - Change this!
SECRET_KEY=your-unique-secret-key-here

# Optional - Whisparr integration
WHISPARR_URL=http://192.168.1.100:6969
WHISPARR_API_KEY=your-whisparr-api-key

# Optional - StashDB integration  
STASHDB_API_KEY=your-stashdb-api-key
```

4. **Start the application:**
```bash
docker-compose up -d
```

5. **Verify installation:**
```bash
# Check container status
docker-compose ps

# Check logs
docker-compose logs stash-filter

# Test web interface
curl http://localhost:5000/health
```

### Method 2: Unraid Template

Perfect for Unraid users who want a simple GUI installation.

1. **Add the template:**
   - Go to **Docker** tab in Unraid
   - Click **Add Container**
   - In **Template** field, paste:
     ```
     https://raw.githubusercontent.com/your-username/stash-filter/main/unraid-template.xml
     ```

2. **Configure container settings:**
   - **Container Name**: `stash-filter`
   - **Repository**: `your-username/stash-filter:latest`
   - **WebUI Port**: `5000`
   - **App Data Path**: `/mnt/user/appdata/stash-filter/data`

3. **Configure environment variables:**
   - **STASH_URL**: Your Stash server URL (e.g., `http://192.168.1.100:9999`)
   - **STASH_API_KEY**: Your Stash API key (get from Stash Settings → Security)
   - **SECRET_KEY**: Generate a unique secret key
   - **WHISPARR_URL**: (Optional) Your Whisparr URL
   - **WHISPARR_API_KEY**: (Optional) Your Whisparr API key

4. **Apply and start:**
   - Click **Apply** to download and start the container
   - Wait for initialization to complete
   - Access via WebUI button or `http://your-unraid-ip:5000`

### Method 3: Manual Docker

For advanced users who want full control over the Docker setup.

1. **Build the image:**
```bash
git clone https://github.com/your-username/stash-filter.git
cd stash-filter
docker build -t stash-filter:latest .
```

2. **Create data directories:**
```bash
mkdir -p data logs config
```

3. **Create environment file:**
```bash
cp .env.example .env
nano .env  # Configure your settings
```

4. **Run the container:**
```bash
docker run -d \
  --name stash-filter \
  --restart unless-stopped \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/config:/app/config \
  --env-file .env \
  stash-filter:latest
```

### Method 4: Development Installation

For developers who want to modify the code.

1. **Clone repository:**
```bash
git clone https://github.com/your-username/stash-filter.git
cd stash-filter
```

2. **Set up Python environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
nano .env  # Configure for development
```

4. **Initialize database:**
```bash
export FLASK_APP=app
export FLASK_ENV=development
flask shell
>>> from app import db
>>> db.create_all()
>>> exit()
```

5. **Start development server:**
```bash
flask run --host=0.0.0.0 --port=5000
```

## Configuration

### Getting API Keys

**Stash API Key:**
1. Open your Stash web interface
2. Go to **Settings** → **Security** → **Authentication**
3. Click **Generate API Key**
4. Copy the generated key to your `.env` file

**Whisparr API Key (Optional):**
1. Open your Whisparr web interface
2. Go to **Settings** → **General**
3. Find the **API Key** field
4. Copy the key to your `.env` file

**StashDB API Key (Optional):**
1. Create account at [stashdb.org](https://stashdb.org)
2. Go to your profile settings
3. Generate an API key
4. Copy the key to your `.env` file

### Network Configuration

**Same Host Installation:**
If Stash-Filter is on the same host as Stash:
```env
STASH_URL=http://localhost:9999
# or
STASH_URL=http://127.0.0.1:9999
```

**Different Host Installation:**
If on different hosts, use the actual IP address:
```env
STASH_URL=http://192.168.1.100:9999
```

**Docker Network:**
If using Docker networks, use service names:
```env
STASH_URL=http://stash-service:9999
```

### Port Configuration

**Default Port (5000):**
```yaml
ports:
  - "5000:5000"
```

**Custom Port:**
```yaml
ports:
  - "8080:5000"  # Access via http://localhost:8080
```

**Multiple Instances:**
```yaml
# Instance 1
ports:
  - "5001:5000"

# Instance 2  
ports:
  - "5002:5000"
```

### Volume Configuration

**Basic Volumes:**
```yaml
volumes:
  - ./data:/app/data          # Database and user data
  - ./logs:/app/logs          # Application logs
  - ./config:/app/config      # Configuration files
```

**Advanced Volumes:**
```yaml
volumes:
  # Named volumes for better management
  - stash-filter-data:/app/data
  - stash-filter-logs:/app/logs
  
  # Custom paths
  - /mnt/storage/stash-filter:/app/data
  - /var/log/stash-filter:/app/logs
  
  # Read-only configuration
  - ./config:/app/config:ro
```

## Post-Installation Setup

### Initial Configuration

1. **Access the web interface:**
   - Open `http://your-server-ip:5000` in your browser
   - You should see the Stash-Filter dashboard

2. **Test connections:**
   - Go to **Settings** → **Connections**
   - Click **Test All Connections**
   - Verify all services show green checkmarks

3. **Sync favorites:**
   - Go to **Dashboard**
   - Click **Sync Favorites from Stash**
   - Verify your favorite performers and studios are imported

4. **Configure filtering:**
   - Go to **Settings** → **Filtering**
   - Set unwanted categories (e.g., "anal", "bdsm")
   - Set required categories if desired (e.g., "lesbian")
   - Configure duration limits

5. **Enable monitoring:**
   - Go to **Performers** or **Studios**
   - Toggle monitoring on for performers/studios you want to track
   - Green indicator means monitoring is active

### First Discovery Run

1. **Manual discovery:**
   - Go to **Dashboard**
   - Click **Run Discovery Now**
   - Monitor the progress and check results

2. **Review discovered scenes:**
   - Go to **Wanted Scenes**
   - Review the scenes that were found
   - Check that filtering worked correctly

3. **Test Whisparr integration (if configured):**
   - Select some wanted scenes
   - Click **Add to Whisparr**
   - Verify scenes appear in Whisparr

## Troubleshooting

### Common Issues

**Connection Refused Errors:**
```bash
# Test network connectivity
docker exec stash-filter curl -f http://stash:9999/graphql

# Check if Stash is accessible
curl -f http://192.168.1.100:9999/graphql
```

**Permission Errors:**
```bash
# Fix data directory permissions
sudo chown -R 1000:1000 ./data ./logs ./config
chmod -R 755 ./data ./logs ./config
```

**Port Already in Use:**
```bash
# Find what's using port 5000
sudo netstat -tlnp | grep :5000

# Use different port in docker-compose.yml
ports:
  - "5001:5000"
```

**Database Locked:**
```bash
# Stop all instances
docker-compose down

# Check for lock files
ls -la data/

# Remove lock files if present
rm -f data/*.db-wal data/*.db-shm

# Restart
docker-compose up -d
```

### Logging and Debugging

**Enable debug logging:**
```env
LOG_LEVEL=DEBUG
FLASK_ENV=development
```

**View logs:**
```bash
# All logs
docker-compose logs stash-filter

# Follow logs in real-time
docker-compose logs -f stash-filter

# Last 100 lines
docker-compose logs --tail 100 stash-filter
```

**Check application health:**
```bash
# Health endpoint
curl http://localhost:5000/health

# Connection test
curl -X POST http://localhost:5000/api/test-connections
```

### Performance Tuning

**For Large Libraries:**
```env
# Reduce batch sizes
MAX_SCENES_PER_CHECK=25

# Increase check interval
DISCOVERY_FREQUENCY_HOURS=48

# Optimize database
SQLITE_CACHE_SIZE=10000
```

**Resource Limits:**
```yaml
# docker-compose.yml
services:
  stash-filter:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

## Security Considerations

### Secret Key Generation

Generate a secure secret key:
```bash
# Method 1: Python
python -c "import secrets; print(secrets.token_hex(32))"

# Method 2: OpenSSL
openssl rand -hex 32

# Method 3: /dev/urandom
head -c 32 /dev/urandom | base64
```

### Network Security

**Restrict Access:**
```yaml
# docker-compose.yml
services:
  stash-filter:
    ports:
      - "127.0.0.1:5000:5000"  # Only localhost access
```

**Use Reverse Proxy:**
```nginx
# nginx config
server {
    listen 443 ssl;
    server_name stash-filter.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Environment Variables

**Never commit sensitive data:**
```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "*.env" >> .gitignore
```

**Use Docker secrets in production:**
```yaml
# docker-compose.yml
services:
  stash-filter:
    secrets:
      - stash_api_key
    environment:
      - STASH_API_KEY_FILE=/run/secrets/stash_api_key

secrets:
  stash_api_key:
    file: ./secrets/stash_api_key.txt
```

## Backup and Maintenance

### Regular Backups

**Database Backup:**
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
cp data/stash_filter.db backups/stash_filter_$DATE.db
find backups/ -name "*.db" -mtime +30 -delete
```

**Full Backup:**
```bash
tar -czf stash_filter_backup_$(date +%Y%m%d).tar.gz \
    data/ logs/ config/ .env docker-compose.yml
```

### Updates

**Update Container:**
```bash
docker-compose pull
docker-compose up -d
```

**Update with Backup:**
```bash
# Backup first
./backup.sh

# Update
docker-compose down
docker-compose pull
docker-compose up -d
```

## Next Steps

After installation:

1. Read the [User Guide](user-guide.md) for daily usage
2. Check [API Documentation](../API.md) for automation
3. Review [Contributing Guide](../CONTRIBUTING.md) to help improve the project
4. Join the community discussions on GitHub

## Getting Help

- **Documentation**: Check all files in the `docs/` directory
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share tips
- **Logs**: Always include relevant log output when asking for help

Remember to remove sensitive information (API keys, IP addresses) when sharing logs or configurations publicly!
