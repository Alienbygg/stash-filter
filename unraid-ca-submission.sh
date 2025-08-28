#!/bin/bash

echo "=== Stash-Filter unRAID CA Submission Helper ==="
echo ""
echo "This script helps you submit Stash-Filter to the unRAID Community Applications."
echo ""

# Check if template exists
if [ ! -f "unraid-template.xml" ]; then
    echo "❌ ERROR: unraid-template.xml not found in current directory"
    echo "Please run this script from your git directory: /mnt/user/appdata/stash-filter/git"
    exit 1
fi

echo "✅ Found unraid-template.xml"
echo ""

echo "📋 **Manual Steps Required:**"
echo ""
echo "1. **Fork the repository:**"
echo "   Go to: https://github.com/selfhosters/unRAID-CA-templates"
echo "   Click 'Fork' button (top right)"
echo ""
echo "2. **Upload template file:**"
echo "   In your forked repo → 'templates' folder → 'Add file' → 'Upload files'"
echo "   Upload: unraid-template.xml"
echo "   Rename to: alienbygg-stash-filter.xml"
echo ""
echo "3. **Create Pull Request:**"
echo "   After upload → 'Create pull request'"
echo "   Use the description below:"
echo ""

echo "---"
echo "**Template Name:** Stash-Filter"
echo "**Docker Hub:** alienbygg/stash-filter" 
echo "**GitHub:** https://github.com/Alienbygg/stash-filter"
echo ""
echo "**Description:**"
echo "Automated content discovery for Stash media servers. Integrates with StashDB and Whisparr for complete media management workflow."
echo ""
echo "**Key Features:**"
echo "- Daily automated scene discovery from StashDB"
echo "- Smart filtering and duplicate detection"  
echo "- Professional web interface with mobile support"
echo "- Complete Whisparr integration for downloads"
echo "- Manual performer/studio search from StashDB"
echo "- Trending scenes discovery with filtering"
echo "- Comprehensive filtered scenes management"
echo "- SQLite database with health monitoring"
echo ""
echo "**Template tested:** Yes, working in production environments"
echo "**Docker image published:** Yes, available on Docker Hub"
echo "**Documentation:** Complete setup guides and API documentation included"
echo "---"
echo ""

echo "4. **Submit the PR** and wait for review!"
echo ""

# Validate template
echo "🔍 **Template Validation:**"
echo ""

# Check required fields
if grep -q "<Repository>alienbygg/stash-filter</Repository>" unraid-template.xml; then
    echo "✅ Docker repository: alienbygg/stash-filter"
else
    echo "❌ Docker repository missing or incorrect"
fi

if grep -q "<Support>https://github.com/Alienbygg/stash-filter" unraid-template.xml; then
    echo "✅ Support URL: GitHub issues"
else
    echo "❌ Support URL missing"
fi

if grep -q "<Project>https://github.com/Alienbygg/stash-filter" unraid-template.xml; then
    echo "✅ Project URL: GitHub repo"
else
    echo "❌ Project URL missing"
fi

if grep -q "<WebUI>http://\[IP\]:\[PORT:5000\]/" unraid-template.xml; then
    echo "✅ WebUI configuration correct"
else
    echo "❌ WebUI configuration incorrect"
fi

if grep -q "Target=\"5000\"" unraid-template.xml; then
    echo "✅ Port 5000 configured"
else
    echo "❌ Port configuration missing"
fi

echo ""
echo "🎯 **Ready for submission!**"
echo ""
echo "💡 **Tips:**"
echo "- The template will be reviewed by CA maintainers"
echo "- They may ask for small changes - just update your PR"
echo "- Once approved, it appears in Community Applications"
echo "- Users can then install with one click!"
echo ""
echo "🔗 **Useful Links:**"
echo "   CA Templates Repo: https://github.com/selfhosters/unRAID-CA-templates"
echo "   Your Docker Hub: https://hub.docker.com/r/alienbygg/stash-filter"
echo "   Your GitHub: https://github.com/Alienbygg/stash-filter"
