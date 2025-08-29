#!/bin/bash

cd /opt/appdata/stash-filter/git

echo "🔥 Committing Trending Performers Feature..."
echo ""

# Check current status
echo "📋 Git Status:"
git status --short

echo ""
echo "📦 Adding all changes..."
git add .

echo ""
echo "💾 Creating commit..."
git commit -m "feat: Add Trending Performers feature with gender filtering and thumbnails

✨ Features Added:
- Trending performers button (🔥 icon) on performers page toolbar
- Gender filtering dropdown (Female, Male, Transgender, Non-Binary, etc.)
- Full-screen modal with responsive performer cards
- Performer thumbnails with overlay badges (scene count, gender)
- Detailed performer metadata (birth year, career, country, ethnicity)  
- One-click 'Add to monitoring' functionality
- Professional styling with hover effects and animations
- Full mobile responsive design

🔧 Technical Implementation:
- New API endpoint: GET /api/get-trending-performers
- Enhanced StashDB API with trending performers method
- Updated performers.html with modal and JavaScript functionality
- Added comprehensive CSS styling for performer cards
- Created images directory for performer placeholders

Files Modified:
- app/stashdb_api.py (trending performers methods)
- app/main.py (API endpoint)
- templates/performers.html (UI and functionality)
- static/style.css (styling and animations)
- static/images/ (directory created)"

echo ""
if [ $? -eq 0 ]; then
    echo "✅ Commit created successfully!"
    echo ""
    echo "🚀 Pushing to remote repository..."
    git push origin main
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 SUCCESS! Trending Performers feature deployed to git repository!"
        echo ""
        echo "🔄 Next Steps:"
        echo "  1. Go to your Unraid Docker tab"
        echo "  2. Find your stash-filter container"  
        echo "  3. Click 'Force Update' or restart container"
        echo "  4. Container will pull latest git changes automatically"
        echo ""
        echo "✨ After container update, you'll see:"
        echo "  🔥 'Trending Performers' button on performers page"
        echo "  🎛️ Gender filtering with dropdown"
        echo "  🖼️ Beautiful performer cards with thumbnails"
        echo "  📱 Mobile-friendly responsive design"
    else
        echo "❌ Error pushing to remote. You may need to push manually."
    fi
else
    echo "❌ Error creating commit"
fi
