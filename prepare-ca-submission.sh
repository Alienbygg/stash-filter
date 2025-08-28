#!/bin/bash

# Navigate to git directory  
cd /mnt/user/appdata/stash-filter/git

echo "=== Preparing unRAID Community Applications Submission ==="
echo ""

# Commit the improved template
git add unraid-template.xml
git commit -m "Improve unRAID template for Community Applications submission

- Streamline overview description for better readability
- Add bullet points for key features  
- Include trending scenes and manual search features
- Improve requirement descriptions
- Optimize for Community Applications display
- Ready for unRAID CA submission"

git push origin main

if [ $? -eq 0 ]; then
    echo "✅ Template improvements pushed to GitHub!"
else
    echo "❌ Failed to push template improvements"
    exit 1
fi

echo ""
echo "🎯 **Now Ready for unRAID Community Applications Submission!**"
echo ""

# Run the submission helper
chmod +x unraid-ca-submission.sh
./unraid-ca-submission.sh

echo ""
echo "🚀 **Next Steps:**"
echo ""
echo "1. **Go to GitHub:** https://github.com/selfhosters/unRAID-CA-templates"
echo "2. **Click 'Fork'** (top right corner)"
echo "3. **In your fork:** Navigate to 'templates' folder"
echo "4. **Upload file:** Add file → Upload → Select 'unraid-template.xml'"
echo "5. **Rename to:** alienbygg-stash-filter.xml"
echo "6. **Commit:** Add commit message 'Add Stash-Filter template'"
echo "7. **Create PR:** Click 'Create Pull Request' button"
echo ""
echo "📝 **Use this PR description:**"
echo ""
echo "**Template Name:** Stash-Filter"
echo "**Docker Hub:** alienbygg/stash-filter"
echo "**GitHub:** https://github.com/Alienbygg/stash-filter"
echo ""
echo "**Description:**"
echo "Automated content discovery for Stash media servers with StashDB integration."
echo ""
echo "**New Features in Latest Version:**"
echo "• Manual performer/studio search from StashDB"
echo "• Trending scenes discovery with filtering"
echo "• Comprehensive filtered scenes management"
echo "• Professional responsive web interface"
echo "• Complete Whisparr integration"
echo ""
echo "**Template Status:**"
echo "✅ Docker image published and tested"
echo "✅ Template validated and working"
echo "✅ Documentation complete"
echo "✅ Icon and assets ready"
echo ""
echo "After submission, the CA team will review and approve your template!"
echo "Once approved, users can install Stash-Filter with one click! 🎉"
