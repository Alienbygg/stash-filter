#!/bin/bash

# Navigate to git directory
cd /mnt/user/appdata/stash-filter/git

echo "=== Fixing Modal Placement Issues ==="

# Add all modified files
git add templates/performers.html
git add templates/studios.html
git add templates/wanted_scenes.html

# Create commit
git commit -m "Fix modal placement for proper Bootstrap functionality

🔧 **Modal Placement Fix:**
- Move all modals from outside content blocks to inside
- Ensures proper HTML structure for Bootstrap modals
- Fix addPerformerModal in performers.html
- Fix addStudioModal in studios.html  
- Fix trendingScenesModal in wanted_scenes.html

🐛 **Resolves Issue:**
- Buttons now properly trigger modal dialogs
- Bootstrap JavaScript can properly initialize modals
- Modals render in correct DOM location

This fixes the issue where 'Add Manually' and 'Trending Scenes' 
buttons appeared to do nothing when clicked."

# Push to GitHub
echo "Pushing modal fixes to GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS: Modal fixes pushed to GitHub!"
    echo ""
    echo "🔧 **Now rebuild your container to test the fixes:**"
    echo "   docker-compose down"
    echo "   docker-compose up -d --build"
    echo ""
    echo "🧪 **Test the buttons:**"
    echo "   1. Go to Performers page → Click 'Add Manually'"
    echo "   2. Go to Studios page → Click 'Add Manually'"
    echo "   3. Go to Wanted Scenes page → Click 'Trending Scenes'"
    echo ""
    echo "All buttons should now open their respective modal dialogs!"
else
    echo ""
    echo "❌ ERROR: Failed to push to GitHub"
fi
