#!/bin/bash

# Navigate to git directory
cd /mnt/user/appdata/stash-filter/git

echo "=== Adding Manual Search and Trending Features ==="

# Add all modified files
git add app/main.py
git add templates/performers.html
git add templates/studios.html
git add templates/wanted_scenes.html

# Check git status
echo "Files to be committed:"
git status --porcelain

# Create comprehensive commit message
git commit -m "Add Manual Search and Trending Features

🔍 **Manual Performer Search & Add:**
- Add 'Add Manually' button to performers page
- Search StashDB for performers without files in Stash
- Modal interface with real-time search results
- Add performers directly to monitoring list
- Prevents duplicate additions with validation

🏢 **Manual Studio Search & Add:**
- Add 'Add Manually' button to studios page  
- Search StashDB for studios without files in Stash
- Modal interface matching performer functionality
- Add studios directly to monitoring list
- Prevents duplicate additions with validation

🔥 **Trending Scenes Discovery:**
- Add 'Trending Scenes' button to wanted scenes page
- Fetch top trending scenes from StashDB
- Apply user's configured filters (categories, duration)
- Display filtered results in attractive card layout
- Select individual or all scenes to add to wanted list
- Shows StashDB links for each scene

🚀 **API Enhancements:**
- /api/search-performers - Search StashDB for performers
- /api/add-performer - Add performer from search results
- /api/search-studios - Search StashDB for studios  
- /api/add-studio - Add studio from search results
- /api/trending-scenes - Get filtered trending scenes

✨ **UI/UX Improvements:**
- Professional modal interfaces with loading states
- Real-time search with enter key support
- Responsive card layouts for trending scenes
- Select all/individual checkboxes
- Error handling and user feedback
- Bootstrap modal integration

These features enable users to discover and monitor content
even without having any files in their Stash instance,
greatly expanding the application's utility for new users."

# Push to GitHub
echo "Pushing to GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS: All new features committed and pushed!"
    echo ""
    echo "🎯 **New Features Added:**"
    echo "   📋 Manual performer search & add from StashDB"
    echo "   🏢 Manual studio search & add from StashDB"
    echo "   🔥 Trending scenes discovery (filtered)"
    echo ""
    echo "🔧 **How to use:**"
    echo "   1. Performers page → 'Add Manually' → Search StashDB"
    echo "   2. Studios page → 'Add Manually' → Search StashDB"  
    echo "   3. Wanted Scenes page → 'Trending Scenes' → Browse filtered results"
    echo ""
    echo "🐳 Rebuild container to see new features:"
    echo "   docker-compose down && docker-compose up -d --build"
else
    echo ""
    echo "❌ ERROR: Failed to push to GitHub"
fi
