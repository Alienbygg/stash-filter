#!/bin/bash

# Navigate to git directory
cd /app/stash-filter/git

echo "🔥 Committing Trending Performers Feature..."

# Add all the files that were updated for the trending performers feature
git add templates/performers.html
git add static/images/performer-placeholder.svg
git add TRENDING_PERFORMERS_FEATURE.md

# Check if there are any changes to commit
if git diff --staged --quiet; then
    echo "❌ No changes to commit"
    exit 0
fi

# Show what will be committed
echo "📋 Files to be committed:"
git diff --staged --name-only

# Commit with descriptive message
git commit -m "feat: Add trending performers with gender filtering and thumbnails

✨ Features:
- Trending performers button on performers page
- Gender-based filtering (female, male, transgender, non-binary)
- Visual cards with performer thumbnails 
- Scene count and performer metadata display
- One-click add to monitoring list
- Auto-loading modal with responsive design

🔧 Technical:
- New API endpoint: /api/get-trending-performers
- Enhanced StashDB integration with GraphQL queries
- SVG placeholder for performers without images
- Proper error handling and loading states

🎯 Benefits:
- Easy discovery of new performers to monitor
- Visual browsing experience with thumbnails
- Efficient filtering by gender preferences
- Seamless integration with existing workflow"

echo "✅ Trending Performers feature committed successfully!"

# Show commit hash
echo "📝 Commit hash: $(git rev-parse --short HEAD)"
