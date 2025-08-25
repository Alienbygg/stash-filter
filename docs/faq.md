# Frequently Asked Questions

## General Questions

### What is Stash-Filter?
Stash-Filter is a Docker application that automatically discovers new scenes for your favorite performers and studios. It integrates with Stash (your media organizer), StashDB (community database), and optionally Whisparr (download manager) to provide a complete content discovery and management solution.

### Do I need coding knowledge to use this?
No! Stash-Filter is designed to be user-friendly with a web interface. If you can install Docker containers (especially on Unraid), you can use this application. Basic understanding of Docker and networking is helpful but not required.

### Is this free?
Yes, Stash-Filter is completely free and open source under the MIT license. You can use it, modify it, and distribute it freely.

### What platforms are supported?
Stash-Filter runs on any platform that supports Docker:
- Linux (Ubuntu, Debian, CentOS, etc.)
- Windows 10/11 with Docker Desktop
- macOS with Docker Desktop
- Unraid (with included template)
- Synology NAS and other NAS systems
- Raspberry Pi (ARM64 images available)

## Installation Questions

### What are the system requirements?
- **Minimum**: 1 CPU core, 512MB RAM, 100MB storage
- **Recommended**: 2+ CPU cores, 1GB+ RAM, 1GB+ storage
- **For large libraries**: 4+ CPU cores, 2GB+ RAM, 10GB+ storage

### Can I run this without Docker?
While Docker is the recommended and supported method, you can run Stash-Filter directly with Python if you prefer. See the [Development Guide](../DEVELOPMENT.md) for Python setup instructions.

### How do I get API keys?
- **Stash API Key**: Go to Stash Settings → Security → Authentication → Generate API Key
- **Whisparr API Key**: Go to Whisparr Settings → General → API Key (copy existing)
- **StashDB API Key**: Create account at stashdb.org → Profile Settings → Generate API Key

### Can I run multiple instances?
Yes! You can run multiple instances for different Stash servers or configurations. Just use different ports and data directories for each instance.

## Usage Questions

### How often does discovery run?
By default, discovery runs daily at 6 AM. You can configure this in Settings → General → Discovery Frequency. You can also trigger manual discovery runs anytime.

### Why aren't any scenes being discovered?
Common reasons:
1. No performers/studios are being monitored (check green indicators)
2. Filtering settings are too restrictive
3. Stash favorites weren't synced properly
4. All discovered scenes already exist in your Stash library
5. StashDB connectivity issues

### How does the filtering work?
Stash-Filter uses multiple filtering methods:
- **Category filters**: Exclude unwanted tags (e.g., "anal", "bdsm")
- **Duration filters**: Only scenes within your preferred length range
- **Existing content**: Automatically excludes scenes you already have
- **Quality filters**: Only scenes meeting your rating criteria

### What's the difference between performers and studios?
- **Performers**: Individual actors/actresses you want to monitor
- **Studios**: Production companies that create content
- You can monitor both types, and scenes are discovered for either

### Can I use this without Whisparr?
Absolutely! Whisparr integration is completely optional. You can use Stash-Filter just for discovery and manage downloads manually or with other tools.

## Technical Questions

### Where is data stored?
All data is stored in the `/app/data` directory inside the container, which you should map to a persistent volume:
- `stash_filter.db` - SQLite database with all application data
- `config.json` - Application configuration
- Log files and temporary data

### How much storage does it use?
- **Application**: ~100MB Docker image
- **Database**: Starts small, grows with discovered scenes (typically 10-100MB)
- **Logs**: Configurable, default rotation keeps them small

### Can I backup my configuration?
Yes! Back up these items:
- The entire `data/` directory (contains database and config)
- Your `.env` file or environment variables
- `docker-compose.yml` file

### What networking ports are used?
- **5000**: Web interface (configurable)
- **Outbound HTTPS**: For API calls to StashDB
- **Outbound HTTP**: For API calls to Stash and Whisparr

### Is my data secure?
- All data stays on your local network
- No telemetry or data collection
- API keys are stored locally only
- Use HTTPS with reverse proxy for additional security

## Configuration Questions

### What categories should I filter?
This is personal preference, but common unwanted categories include:
- `anal`, `bdsm`, `hardcore`, `rough`, `gangbang`
- Check StashDB tags to see what categories exist

### How do I find my Stash GraphQL endpoint?
Your Stash GraphQL endpoint is typically:
- `http://your-stash-ip:9999/graphql`
- Test it by visiting this URL in your browser

### Should I use automatic Whisparr adding?
- **Yes**: If you trust your filtering and want full automation
- **No**: If you prefer to review scenes before downloading

### How many scenes should I allow per check?
- **Small libraries**: 100+ scenes per check is fine
- **Large libraries**: Start with 25-50 to avoid overwhelming the system
- **Testing**: Use 10-20 while setting up and testing filters

## Troubleshooting Questions

### Stash-Filter can't connect to Stash
1. Verify Stash is running and accessible
2. Check if API key is correct and not expired
3. Test the URL manually in your browser
4. Check firewall and network settings
5. Ensure Docker networking is properly configured

### Discovery runs but finds no scenes
1. Check if performers/studios are monitored (green indicators)
2. Review filtering settings - they might be too strict
3. Verify Stash favorites are synced
4. Check if StashDB is accessible
5. Look at discovery logs for specific errors

### Whisparr integration isn't working
1. Test Whisparr connection in Settings
2. Verify API key is correct
3. Check if quality profile exists in Whisparr
4. Ensure indexers are configured in Whisparr
5. Review Whisparr logs for errors

### The web interface won't load
1. Check if container is running: `docker ps`
2. Check container logs: `docker logs stash-filter`
3. Verify port mapping is correct
4. Test if health endpoint works: `curl http://localhost:5000/health`
5. Check for port conflicts with other services

### Database errors or corruption
1. Stop all instances of Stash-Filter
2. Check if database file exists and has proper permissions
3. Try database repair: `sqlite3 data/stash_filter.db "PRAGMA integrity_check;"`
4. Restore from backup if needed
5. As last resort, delete database (loses all data but rebuilds clean)

## Performance Questions

### Stash-Filter is using too much CPU/RAM
1. Reduce concurrent requests in settings
2. Decrease max scenes per check
3. Increase discovery interval (run less frequently)
4. Check for infinite loops in logs
5. Consider resource limits in Docker

### Discovery takes too long to complete
1. Reduce the number of monitored performers/studios
2. Lower max scenes per check
3. Optimize your Stash database
4. Check network connectivity to StashDB
5. Enable debug logging to identify bottlenecks

### Database is growing too large
1. Regular database vacuum: `VACUUM;`
2. Clean up old discovery logs
3. Remove unmonitored performers/studios
4. Archive old wanted scenes
5. Consider more restrictive filtering

## Integration Questions

### Can I integrate with other *arr applications?
Currently, only Whisparr is supported, but the API allows custom integrations. Community contributions for other *arr apps are welcome!

### Can I use this with Plex/Jellyfin/Emby?
Stash-Filter works with Stash, which can organize media for any media server. It doesn't directly integrate with Plex/Jellyfin/Emby.

### Is there a mobile app?
No dedicated mobile app, but the web interface is responsive and works well on mobile browsers.

### Can I get notifications?
Currently, notifications are limited to the web interface. Webhook support is planned for future releases to enable email/Discord/Slack notifications.

## Development Questions

### Can I contribute to the project?
Yes! Contributions are very welcome. See the [Contributing Guide](../CONTRIBUTING.md) for details on:
- Reporting bugs
- Suggesting features  
- Contributing code
- Improving documentation

### How do I request a feature?
1. Check existing GitHub issues first
2. Create a new issue with the "enhancement" label
3. Describe your use case and proposed solution
4. Be open to discussion about implementation

### Can I modify the code for my needs?
Absolutely! The MIT license allows you to modify and redistribute the code. Consider contributing useful changes back to the community.

## Common Error Messages

### "Connection refused to stash:9999"
- Stash is not running or not accessible
- Check Stash URL configuration
- Verify network connectivity

### "Invalid API key"
- API key is incorrect or expired
- Regenerate API key in source application
- Check for typos in configuration

### "Database is locked"
- Multiple instances are trying to access database
- Stop all instances and restart one
- Check for hung processes

### "Rate limit exceeded"
- Too many requests to external APIs
- Increase delays between requests
- Check API quotas and limits

### "No such table: performers"
- Database not initialized properly
- Delete database file and restart (loses data)
- Check file permissions on data directory

## Getting More Help

Still need help? Here are your options:

1. **Search GitHub Issues**: Someone might have had the same problem
2. **GitHub Discussions**: Ask questions and get community help
3. **Create an Issue**: Report bugs with detailed information
4. **Check Logs**: Most problems show up in application logs first
5. **Review Configuration**: Double-check all settings are correct

When asking for help, always include:
- Stash-Filter version
- Docker/system information
- Relevant log excerpts (remove sensitive data!)
- Steps to reproduce the issue
- What you expected vs. what happened

---

*Don't see your question here? Consider contributing to this FAQ by creating an issue or discussion on GitHub!*
