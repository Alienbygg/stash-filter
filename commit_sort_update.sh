#!/bin/bash

# Navigate to git directory
cd /mnt/user/appdata/stash-filter/git

echo "=== Updating Wanted Scenes Sorting ==="

# Add the modified files
git add app/main.py
git add templates/wanted_scenes.html

# Create commit
git commit -m "Change wanted scenes sorting to newest release date

🗓️ **Sort by Release Date:**
- Change wanted scenes ordering from added_date to release_date DESC
- Scenes with newest release dates now appear first
- Fallback to added_date for scenes without release dates
- Uses nullslast() to put unknown release dates at bottom

🎨 **UI Improvements:**
- Make Release Date column header bold with down arrow indicator  
- Style release dates in blue to show primary sort
- Add 'Sorted by newest release date' text to card header
- Make release date values bold for better visibility

This ensures users see the most recently released scenes first,
making it easier to find the latest content from their monitored
performers and studios."

# Push to GitHub
echo "Pushing to GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS: Wanted scenes now sort by newest release date!"
    echo ""
    echo "🔍 Changes made:"
    echo "   - Wanted scenes now ordered by release date (newest first)"
    echo "   - Release Date column is highlighted as primary sort"
    echo "   - Unknown release dates appear at the bottom"
    echo ""
    echo "🐳 Rebuild your container to see the changes:"
    echo "   docker-compose down && docker-compose up -d --build"
else
    echo ""
    echo "❌ ERROR: Failed to push to GitHub"
fi
