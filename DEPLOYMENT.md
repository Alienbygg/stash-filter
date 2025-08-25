# Deployment Guide

This guide covers different ways to deploy Stash-Filter for production use.

## Prerequisites

- Docker and Docker Compose installed
- Access to a Stash instance
- Basic understanding of Docker networking
- (Optional) Whisparr instance for automatic downloads
- (Optional) StashDB API key for enhanced features

## Quick Deployment Options

### Option 1: Docker Compose (Recommended)

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/stash-filter.git
cd stash-filter
```

2. **Configure environment:**
```bash
cp .env.example .env
nano .env  # Edit with your settings
```

3. **Start the application:**
```bash
docker-compose up -d
```

4. **Access the web interface:**
```
http://your-server-ip:5000
```

### Option 2: Unraid (Easiest)

1. **Add the template:**
   - Go to **Docker** tab in Unraid
   - Click **Add Container**
   - In **Template** field, enter:
     ```
     https://raw.githubusercontent.com/your-username/stash-filter/main/unraid-template.xml
     ```

2. **Configure settings:**
   - Set your **Stash URL** and **API Key**
   - Configure optional Whisparr integration
   - Choose your data paths

3. **Apply and start the container**

### Option 3: Manual Docker

1. **Build the image:**
```bash
docker build -t stash-filter .
```

2. **Run the container:**
```bash
docker run -d \
  --name stash-filter \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e STASH_URL=http://your-stash-ip:9999 \
  -e STASH_API_KEY=your-api-key \
  stash-filter
```

## Production Configuration

### Environment Variables

**Required:**
```env
STASH_URL=http://192.168.1.100:9999
STASH_API_KEY=your-stash-api-key-here
SECRET_KEY=change-this-in-production-random-string
```

**Optional:**
```env
WHISPARR_URL=http://192.168.1.100:6969
WHISPARR_API_KEY=your-whisparr-api-key
STASHDB_API_KEY=your-stashdb-api-key
LOG_LEVEL=INFO
DATABASE_PATH=/app/data/stash_filter.db
FLASK_ENV=production
```

### Security Recommendations

1. **Change the secret key:**
   ```bash
   # Generate a secure secret key
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Use environment variables for sensitive data:**
   - Never hardcode API keys
   - Use Docker secrets in swarm mode
   - Consider using external secret management

3. **Network security:**
   - Run on isolated Docker network
   - Use reverse proxy (nginx/traefik) with SSL
   - Restrict access to trusted networks only

### Performance Tuning

**For large libraries (10,000+ scenes):**
```env
# Limit concurrent processing
MAX_SCENES_PER_CHECK=50

# Reduce check frequency
DISCOVERY_FREQUENCY_HOURS=48

# Optimize database
SQLITE_CACHE_SIZE=10000
```

**For high-traffic scenarios:**
```yaml
# docker-compose.yml
services:
  stash-filter:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
```

## Advanced Deployment

### Docker Swarm

```yaml
# docker-stack.yml
version: '3.8'
services:
  stash-filter:
    image: your-username/stash-filter:latest
    ports:
      - "5000:5000"
    environment:
      - STASH_URL=http://stash:9999
      - STASH_API_KEY_FILE=/run/secrets/stash_api_key
    secrets:
      - stash_api_key
    volumes:
      - stash-filter-data:/app/data
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

secrets:
  stash_api_key:
    external: true

volumes:
  stash-filter-data:
```

Deploy:
```bash
docker secret create stash_api_key stash_key.txt
docker stack deploy -c docker-stack.yml stash-filter
```

### Kubernetes

```yaml
# kubernetes-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: stash-filter
spec:
  replicas: 1
  selector:
    matchLabels:
      app: stash-filter
  template:
    metadata:
      labels:
        app: stash-filter
    spec:
      containers:
      - name: stash-filter
        image: your-username/stash-filter:latest
        ports:
        - containerPort: 5000
        env:
        - name: STASH_URL
          value: "http://stash-service:9999"
        - name: STASH_API_KEY
          valueFrom:
            secretKeyRef:
              name: stash-secrets
              key: api-key
        volumeMounts:
        - name: data
          mountPath: /app/data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: stash-filter-data
---
apiVersion: v1
kind: Service
metadata:
  name: stash-filter-service
spec:
  selector:
    app: stash-filter
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
```

### Reverse Proxy with SSL

**Nginx:**
```nginx
server {
    listen 443 ssl http2;
    server_name stash-filter.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Traefik (Docker Compose):**
```yaml
version: '3.8'
services:
  traefik:
    image: traefik:v2.10
    command:
      - "--api.dashboard=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--providers.docker=true"
      - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.email=your@email.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "./letsencrypt:/letsencrypt"

  stash-filter:
    image: your-username/stash-filter:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.stash-filter.rule=Host(`stash-filter.yourdomain.com`)"
      - "traefik.http.routers.stash-filter.entrypoints=websecure"
      - "traefik.http.routers.stash-filter.tls.certresolver=letsencrypt"
```

## Monitoring and Logging

### Health Monitoring

```bash
# Health check script
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health)
if [ $response -eq 200 ]; then
    echo "✅ Stash-Filter is healthy"
else
    echo "❌ Stash-Filter is unhealthy (HTTP $response)"
    exit 1
fi
```

### Log Management

**Docker Compose with logging:**
```yaml
services:
  stash-filter:
    image: your-username/stash-filter:latest
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**Centralized logging with Loki:**
```yaml
services:
  stash-filter:
    image: your-username/stash-filter:latest
    logging:
      driver: loki
      options:
        loki-url: "http://localhost:3100/loki/api/v1/push"
        loki-batch-size: "400"
```

### Metrics with Prometheus

Add to your application:
```python
# app/monitoring.py
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('stash_filter_requests_total', 'Total requests')
REQUEST_LATENCY = Histogram('stash_filter_request_duration_seconds', 'Request latency')

@app.route('/metrics')
def metrics():
    return generate_latest()
```

## Backup and Recovery

### Database Backup

```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_PATH="/app/data/stash_filter.db"

# Create backup
sqlite3 $DB_PATH ".backup $BACKUP_DIR/stash_filter_$DATE.db"

# Keep only last 30 days
find $BACKUP_DIR -name "stash_filter_*.db" -mtime +30 -delete

echo "Backup completed: stash_filter_$DATE.db"
```

**Automated backup with cron:**
```bash
# Add to crontab
0 2 * * * /path/to/backup-script.sh
```

### Configuration Backup

```bash
# Backup configuration
tar -czf config_backup_$(date +%Y%m%d).tar.gz \
  .env \
  docker-compose.yml \
  data/config.json
```

## Troubleshooting

### Common Issues

**1. Connection refused to Stash:**
```bash
# Test connectivity
docker exec stash-filter curl -f http://stash:9999/graphql
```

**2. Database locked errors:**
```bash
# Check for multiple instances
docker ps | grep stash-filter

# Stop all instances and restart
docker-compose down && docker-compose up -d
```

**3. Permission issues:**
```bash
# Fix data directory permissions
sudo chown -R 1000:1000 ./data ./logs
```

**4. High memory usage:**
```bash
# Monitor memory usage
docker stats stash-filter

# Reduce batch sizes in .env
MAX_SCENES_PER_CHECK=25
```

### Performance Diagnostics

```bash
# Monitor container resources
docker stats stash-filter

# Check logs for errors
docker logs stash-filter --tail 100

# Database performance
sqlite3 data/stash_filter.db "ANALYZE; .timer on; SELECT COUNT(*) FROM scenes;"
```

## Scaling Considerations

### Horizontal Scaling

For multiple Stash instances:
```yaml
# docker-compose.yml
services:
  stash-filter-main:
    image: your-username/stash-filter:latest
    environment:
      - STASH_URL=http://stash-main:9999
      - INSTANCE_NAME=main

  stash-filter-backup:
    image: your-username/stash-filter:latest
    environment:
      - STASH_URL=http://stash-backup:9999
      - INSTANCE_NAME=backup
```

### Load Balancing

```nginx
upstream stash-filter {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
}

server {
    location / {
        proxy_pass http://stash-filter;
    }
}
```

## Migration

### From Development to Production

1. **Export development data:**
```bash
docker exec stash-filter-dev sqlite3 /app/data/stash_filter.db ".dump" > prod_migration.sql
```

2. **Import to production:**
```bash
docker exec -i stash-filter-prod sqlite3 /app/data/stash_filter.db < prod_migration.sql
```

### Version Upgrades

1. **Backup current installation**
2. **Pull new image version**
3. **Update configuration if needed**
4. **Restart services**
5. **Verify functionality**

```bash
# Upgrade script
#!/bin/bash
docker-compose down
docker pull your-username/stash-filter:latest
docker-compose up -d
docker logs stash-filter --tail 50
```

## Support

For deployment issues:
- Check [DEVELOPMENT.md](DEVELOPMENT.md) for local setup
- Review logs: `docker logs stash-filter`
- Open an issue on GitHub with your configuration
- Join the community discussions

Remember to remove sensitive information (API keys, IPs) when seeking help!
