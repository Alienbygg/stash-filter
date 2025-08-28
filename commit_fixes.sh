#!/bin/bash

# Navigate to git directory
cd /mnt/user/appdata/stash-filter/git

echo "=== Committing Stash Filter Performance and Stability Fixes ==="

# Show what files have been changed
echo "Changed files:"
git status --porcelain

# Add all the modified files
git add app/main.py
git add scripts/entrypoint.sh  
git add app/scheduler.py
git add app/discovery.py

# Commit with comprehensive message
git commit -m "Performance and Stability Improvements

🐛 SQLAlchemy Compatibility Fix:
- Remove deprecated checkfirst=True parameter from db.create_all()
- Fixes TypeError in SQLAlchemy 2.x compatibility
- Resolves Gunicorn worker boot failures

⏱️ Worker Timeout Prevention:
- Increase Gunicorn timeout from 60s to 300s (5 minutes)
- Add graceful timeout handling
- Prevents worker timeouts during discovery process

📝 Scheduler Context Fix:  
- Fix application context error in scheduler logging
- Add defensive logging with fallback to standard logging
- Prevents 'Working outside of application context' errors

🚀 Discovery Process Optimization:
- Limit performers per run (max 10) to prevent timeouts
- Limit studios per run (max 5) due to higher scene counts  
- Reduce page limits: 5 pages for performers, 10 for studios
- Add periodic commits during processing to prevent data loss
- Add progress logging for better monitoring

These changes ensure reliable operation without worker timeouts
while maintaining full functionality for content discovery."

# Push to GitHub
echo "Pushing to GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS: All fixes committed and pushed to GitHub!"
    echo ""
    echo "🐳 Ready to rebuild your Docker container:"
    echo "   docker-compose down"
    echo "   docker-compose build --no-cache"
    echo "   docker-compose up -d"
    echo ""
    echo "🔍 Monitor with: docker-compose logs -f stash-filter"
else
    echo ""
    echo "❌ ERROR: Failed to push to GitHub"
    echo "Check your git configuration and try again"
fi
