# User Guide

This comprehensive guide covers how to use Stash-Filter for daily content discovery and management.

## Getting Started

### First Login

After installation, access Stash-Filter at `http://your-server-ip:5000`. You'll see the main dashboard with several sections:

- **Dashboard**: Overview and quick actions
- **Performers**: Manage monitored performers  
- **Studios**: Manage monitored studios
- **Wanted Scenes**: Review discovered content
- **Settings**: Configure the application

### Initial Setup

1. **Test Connections**
   - Go to **Settings** → **Connections**
   - Click **Test All Connections**
   - Verify green checkmarks for Stash and other services

2. **Sync Your Favorites**
   - Return to **Dashboard**
   - Click **Sync Favorites from Stash**
   - This imports your existing Stash favorites

3. **Configure Filtering**
   - Go to **Settings** → **Filtering**
   - Set up content filters (see [Filtering Guide](#content-filtering))

## Core Features

### Content Discovery

Stash-Filter automatically searches for new scenes from your monitored performers and studios using StashDB.

**How Discovery Works:**
1. Checks each monitored performer/studio for new scenes
2. Filters results based on your preferences
3. Excludes scenes you already own
4. Adds qualifying scenes to your wanted list
5. Optionally adds wanted scenes to Whisparr

**Manual Discovery:**
- Go to **Dashboard**
- Click **Run Discovery Now**
- Monitor progress in the notification area

**Automatic Discovery:**
- Runs daily at 6 AM by default
- Configure frequency in **Settings** → **General**
- View last run results on Dashboard

### Managing Performers

**Adding Performers:**
1. Ensure the performer is marked as favorite in Stash
2. Run **Sync Favorites** to import them
3. Toggle monitoring on/off as needed

**Performer Management:**
- **Green indicator**: Monitoring enabled
- **Gray indicator**: Monitoring disabled
- **Last Checked**: Shows when performer was last scanned
- **Scene Count**: Total scenes discovered for this performer

**Performer Details:**
Click on any performer to view:
- StashDB profile link
- Recent discovered scenes
- Monitoring history
- Related wanted scenes

### Managing Studios

Studio management works similarly to performers:

**Studio Hierarchy:**
- Some studios have parent/child relationships
- Child studios inherit monitoring from parents
- Configure this behavior in settings

**Studio Information:**
- Network/parent studio relationships
- Total scenes in your library
- Recently discovered content
- Production frequency

### Wanted Scenes Management

The **Wanted Scenes** page shows all discovered content awaiting your decision.

**Scene Information Display:**
- **Title**: Scene name from StashDB
- **Performer(s)**: Featured performers
- **Studio**: Production studio
- **Release Date**: Original release date
- **Duration**: Runtime in minutes
- **Status**: Current download status
- **Actions**: Available operations

**Scene Actions:**
- **Add to Whisparr**: Queue for download
- **Remove**: Remove from wanted list
- **View Details**: See full scene information
- **Mark as Owned**: If you acquire it elsewhere

**Bulk Operations:**
- Select multiple scenes using checkboxes
- **Add All to Whisparr**: Batch add selected scenes
- **Remove All**: Batch remove selected scenes
- **Export List**: Export scene list to CSV

### Content Filtering

Powerful filtering system to ensure you only see relevant content.

**Category Filtering:**
- **Unwanted Categories**: Automatically filter out (e.g., "anal", "bdsm")
- **Required Categories**: Must include at least one (e.g., "lesbian")
- Categories are pulled from StashDB tags

**Duration Filtering:**
- **Minimum Duration**: Exclude scenes shorter than X minutes
- **Maximum Duration**: Exclude scenes longer than X minutes
- Useful for filtering out trailers or very long content

**Quality Filtering:**
- **Minimum Rating**: Only include highly-rated scenes
- **Studio Whitelist/Blacklist**: Include/exclude specific studios
- **Performer Filtering**: Advanced performer-specific rules

**Custom Filters:**
Create advanced filtering rules using:
- Release date ranges
- Tag combinations  
- Performer combinations
- Studio networks

### Whisparr Integration

Seamless integration with Whisparr for automatic downloads.

**Setup Requirements:**
1. Configure Whisparr URL and API key in Settings
2. Ensure Whisparr can access your download client
3. Configure quality profiles in Whisparr
4. Set up indexers in Whisparr

**Automatic Mode:**
- Enable **Auto-add to Whisparr** in Settings
- All qualifying discovered scenes are automatically added
- Monitor progress in Whisparr interface

**Manual Mode:**
- Review wanted scenes first
- Manually select scenes to add to Whisparr
- Better control over what gets downloaded

**Download Status Tracking:**
- **Wanted**: Added to Whisparr, awaiting download
- **Searching**: Whisparr is searching indexers
- **Downloading**: Currently downloading
- **Downloaded**: Successfully downloaded
- **Failed**: Download failed, check Whisparr logs

## Settings Configuration

### General Settings

**Discovery Settings:**
- **Enable Discovery**: Master on/off switch
- **Discovery Frequency**: How often to run (hours)
- **Max Scenes Per Check**: Limit results per discovery run
- **Discovery Time**: When to run automatic discovery

**Performance Settings:**
- **Concurrent Requests**: Number of parallel API calls
- **Request Timeout**: Timeout for external API calls  
- **Rate Limiting**: Delay between requests

### Connection Settings

**Stash Configuration:**
- **Stash URL**: Your Stash server address
- **API Key**: Stash API key from Settings → Security
- **GraphQL Endpoint**: Usually `/graphql` (default)

**StashDB Configuration:**
- **API Key**: Optional, for enhanced features
- **Rate Limit**: Requests per minute limit
- **Default Performer Search**: Search preferences

**Whisparr Configuration:**
- **Whisparr URL**: Your Whisparr server address
- **API Key**: Whisparr API key from Settings → General
- **Quality Profile**: Default quality profile name
- **Root Folder**: Download directory path

### Filtering Settings

**Content Filters:**
```
Unwanted Categories: anal, bdsm, hardcore, rough
Required Categories: lesbian, softcore  
Min Duration: 15 minutes
Max Duration: 120 minutes
Min Rating: 7.0
```

**Studio Preferences:**
- **Preferred Networks**: Studios to prioritize
- **Blocked Studios**: Studios to always exclude
- **Quality Thresholds**: Rating requirements by studio

**Performer Preferences:**
- **Favorite Tags**: Preferred scene types per performer
- **Exclusion Rules**: Content to skip for specific performers
- **Priority Levels**: High/normal/low priority performers

### Notification Settings

**Email Notifications** (if configured):
- New scenes discovered
- Download completions
- Error notifications
- Weekly/monthly summaries

**Webhook Notifications:**
- POST to custom URL with discovery results
- Slack/Discord integration
- Custom automation triggers

## Advanced Usage

### Custom Schedules

Beyond daily discovery, create custom schedules:

**Weekly Deep Discovery:**
- More thorough search once per week
- Higher scene count limits
- Expanded date ranges

**Performer-Specific Schedules:**
- VIP performers checked more frequently
- New performer intensive monitoring
- Seasonal performer activation

### API Integration

Automate Stash-Filter using the REST API:

**Common API Uses:**
```bash
# Trigger discovery
curl -X POST http://localhost:5000/api/run-discovery

# Check status
curl http://localhost:5000/health

# Get wanted scenes
curl http://localhost:5000/api/wanted-scenes

# Add scene to Whisparr
curl -X POST http://localhost:5000/api/add-to-whisparr \
  -H "Content-Type: application/json" \
  -d '{"wanted_id": 123}'
```

### Database Management

**Backup Database:**
```bash
# Manual backup
cp data/stash_filter.db backups/backup_$(date +%Y%m%d).db

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
sqlite3 data/stash_filter.db ".backup backups/stash_filter_$DATE.db"
find backups/ -name "*.db" -mtime +30 -delete
```

**Database Maintenance:**
- **Vacuum**: Optimize database size monthly
- **Cleanup**: Remove old discovery logs
- **Analyze**: Update query statistics
- **Integrity Check**: Verify database health

### Performance Optimization

**Large Library Optimization:**
```env
# Reduce batch sizes
MAX_SCENES_PER_CHECK=50

# Increase timeouts
REQUEST_TIMEOUT=60

# Database tuning
SQLITE_CACHE_SIZE=20000
SQLITE_TEMP_STORE=memory
```

**Network Optimization:**
- Use wired connection for servers
- Configure quality DNS servers
- Consider local StashDB mirror
- Optimize Docker networking

## Troubleshooting

### Common Issues

**No Scenes Discovered:**
1. Check performer/studio monitoring is enabled
2. Verify Stash favorites are synced
3. Review filtering settings (too restrictive?)
4. Check StashDB connectivity
5. Review discovery logs

**Discovery Runs But No Results:**
1. Check if scenes already exist in Stash
2. Verify filtering criteria aren't too strict
3. Check discovery date range settings
4. Review performer activity on StashDB

**Whisparr Integration Issues:**
1. Test Whisparr connection in Settings
2. Verify API key permissions
3. Check quality profile exists
4. Ensure indexers are configured
5. Review Whisparr logs

**Performance Issues:**
1. Reduce concurrent requests
2. Increase discovery frequency (less frequent)
3. Limit max scenes per check
4. Check database size and vacuum
5. Review system resources

### Error Messages

**"Connection refused":**
- Service is not running or accessible
- Check firewall settings
- Verify URL and port configuration

**"Authentication failed":**
- Invalid or expired API key
- Check API key configuration
- Regenerate API keys if needed

**"Database locked":**
- Multiple instances running
- Backup/restore in progress
- Stop all instances and restart

**"Rate limit exceeded":**
- Too many requests to external APIs
- Increase delays between requests
- Check API quotas and limits

### Log Analysis

**Enable Debug Logging:**
```env
LOG_LEVEL=DEBUG
```

**Important Log Sections:**
- **Startup**: Connection testing and initialization
- **Discovery**: Scene search and filtering results
- **API Calls**: External service interactions
- **Database**: Query performance and errors
- **Filtering**: Why scenes were included/excluded

**Log Rotation:**
Configure log rotation to prevent disk space issues:
```yaml
# docker-compose.yml
logging:
  driver: "json-file" 
  options:
    max-size: "10m"
    max-file: "3"
```

## Best Practices

### Setup Best Practices

1. **Start Small**: Begin monitoring a few performers/studios
2. **Test Filtering**: Run manual discovery to verify filters
3. **Monitor Resources**: Check CPU/memory usage initially
4. **Backup Configuration**: Save working configurations
5. **Document Changes**: Keep track of settings that work

### Maintenance Best Practices

1. **Regular Updates**: Keep Docker images current
2. **Monitor Logs**: Weekly log review for issues
3. **Database Maintenance**: Monthly vacuum and backup
4. **Performance Review**: Quarterly optimization review
5. **Configuration Backup**: After any major changes

### Security Best Practices

1. **Change Default Secrets**: Generate unique secret keys
2. **Limit Network Access**: Use firewall rules
3. **Regular Updates**: Apply security patches promptly
4. **API Key Rotation**: Rotate keys quarterly
5. **Log Security**: Monitor for unusual activity

### Content Management Best Practices

1. **Review Regularly**: Weekly wanted scenes review
2. **Adjust Filters**: Monthly filter optimization
3. **Clean Up**: Remove unwanted/duplicate content
4. **Monitor Storage**: Ensure adequate disk space
5. **Quality Control**: Verify downloaded content quality

## Tips and Tricks

### Discovery Optimization

**Timing Tips:**
- Run discovery during off-peak hours
- Stagger multiple instances if running several
- Consider timezone differences for release times

**Filter Efficiency:**
- Start with broad filters, then narrow down
- Use required categories to reduce false positives
- Adjust duration limits based on content preferences

**Performance Tips:**
- Monitor slow performers/studios and adjust frequency
- Use performer aliases for better matching
- Keep performer lists current and remove inactive ones

### Whisparr Integration Tips

**Setup Tips:**
- Create separate quality profiles for different content types
- Use proper naming conventions for organization
- Configure post-processing scripts for automation

**Management Tips:**
- Regular Whisparr database cleanup
- Monitor indexer performance and adjust
- Use download client categories for organization

### Organization Tips

**Content Organization:**
- Use consistent tagging in Stash
- Maintain performer aliases and names
- Regular library cleanup and deduplication

**Workflow Organization:**
- Set specific times for reviewing wanted scenes
- Create routine maintenance schedules
- Document successful configurations and workflows

## Getting Help

### Self-Help Resources

1. **Check Logs**: Most issues show up in logs first
2. **Review Settings**: Verify all configurations are correct
3. **Test Connections**: Use built-in connection tests
4. **Read Documentation**: This guide covers most scenarios
5. **Check GitHub Issues**: Someone may have had the same problem

### Community Support

1. **GitHub Discussions**: Ask questions and share experiences
2. **Issue Reports**: Report bugs with detailed information
3. **Feature Requests**: Suggest improvements
4. **Contributing**: Help improve documentation and code

### Reporting Issues

**Include This Information:**
- Stash-Filter version
- Docker/system information  
- Relevant log excerpts (remove sensitive data!)
- Steps to reproduce the issue
- Expected vs actual behavior
- Configuration details (sanitized)

**Log Collection:**
```bash
# Collect recent logs
docker logs stash-filter --tail 200 > logs.txt

# Remove sensitive data before sharing
sed -i 's/api-key-[a-z0-9]*/[REDACTED-API-KEY]/g' logs.txt
```

Remember: Always remove sensitive information (API keys, IP addresses, personal data) before sharing logs or configurations publicly!
