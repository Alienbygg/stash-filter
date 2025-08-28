# 🔧 Stash-Filter: MAJOR UPDATE & BUG FIXES

## 🚨 **CRITICAL FIX**: Database Error Resolution

If you're getting this error when adding performers:
```
Error: (sqlite3.IntegrityError) NOT NULL constraint failed: performers.stash_id
```

**This has been FIXED!** Follow the [Database Migration](#database-migration) section below.

## 🎉 **NEW FEATURES ADDED**

### ✨ **Enhanced Performer Management**
- **Search StashDB**: Search and add performers directly from StashDB without needing them in your local Stash
- **Manual Addition**: Add performers that aren't in your Stash favorites
- **StashDB Links**: Direct links to performer pages on StashDB
- **Fixed Database Schema**: No more "NOT NULL constraint failed" errors

### 🔥 **Trending Scenes Dashboard**
- **Visual Scene Cards**: Beautiful thumbnail view of trending scenes
- **Scene Thumbnails**: High-quality images loaded from StashDB
- **Quick Actions**: Direct "View on StashDB" and "Add to Wanted" buttons
- **Responsive Design**: Works perfectly on mobile and desktop
- **Auto-Refresh**: Keep up with the latest trending content

### 🎨 **Enhanced UI/UX**
- **Modern Scene Cards**: Hover effects and smooth animations
- **Improved Styling**: Better visual hierarchy and spacing
- **Mobile Responsive**: All new features work great on mobile
- **Loading States**: Clear feedback when data is being fetched

---

## 🔧 **Database Migration**

### **Quick Fix (Automated)**

1. **Run the migration script**:
   ```bash
   cd /path/to/stash-filter
   chmod +x fix_database.sh
   ./fix_database.sh
   ```

2. **Restart your Docker container**:
   ```bash
   docker restart stash-filter
   ```

3. **Test the fix**: Try adding a performer using the "Add Manually" button

### **Manual Fix (If needed)**

If the automated script doesn't work:

1. **Stop your container**:
   ```bash
   docker stop stash-filter
   ```

2. **Run the Python migration**:
   ```bash
   python3 migrate_stash_id.py /path/to/your/stash_filter.db
   ```

3. **Start your container**:
   ```bash
   docker start stash-filter
   ```

---

## 📸 **Screenshots**

### **New Performer Search**
![Performer Search](docs/images/performer-search.png)
*Search and add performers directly from StashDB*

### **Trending Scenes Dashboard**
![Trending Scenes](docs/images/trending-scenes.png)
*Beautiful visual dashboard with scene thumbnails*

### **Enhanced Performer List**
![Performer List](docs/images/performer-list.png)
*Updated performer management with StashDB links*

---

## 🚀 **Installation & Setup**

### **Docker Compose (Recommended)**

```yaml
version: '3.8'
services:
  stash-filter:
    image: your-registry/stash-filter:latest
    container_name: stash-filter
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    environment:
      - STASH_URL=http://your-stash-url:9999
      - STASHDB_URL=https://stashdb.org
      - STASHDB_API_KEY=your-stashdb-api-key
      - WHISPARR_URL=http://your-whisparr-url:6969
      - WHISPARR_API_KEY=your-whisparr-api-key
      - DATABASE_PATH=/app/data/stash_filter.db
      - LOG_LEVEL=INFO
    restart: unless-stopped
```

### **Environment Variables**

| Variable | Description | Required |
|----------|-------------|----------|
| `STASH_URL` | Your Stash instance URL | ✅ Yes |
| `STASHDB_URL` | StashDB URL (usually https://stashdb.org) | ✅ Yes |
| `STASHDB_API_KEY` | Your StashDB API key | ✅ Yes |
| `WHISPARR_URL` | Your Whisparr instance URL | ✅ Yes |
| `WHISPARR_API_KEY` | Your Whisparr API key | ✅ Yes |
| `DATABASE_PATH` | SQLite database location | ❌ No (default: `/app/data/stash_filter.db`) |
| `LOG_LEVEL` | Logging level | ❌ No (default: `INFO`) |

---

## 🔄 **What's Fixed**

### **Database Issues**
- ✅ **Fixed**: `NOT NULL constraint failed: performers.stash_id` error
- ✅ **Fixed**: Manual performer additions now work correctly
- ✅ **Fixed**: StashDB performers can be added without local Stash entries

### **UI/UX Improvements**
- ✅ **Added**: Performer search modal with StashDB integration
- ✅ **Added**: Trending scenes with thumbnails on dashboard
- ✅ **Added**: Direct StashDB links on performer results
- ✅ **Improved**: Scene cards with hover effects and animations
- ✅ **Enhanced**: Mobile responsiveness across all pages

### **Performance Enhancements**
- ✅ **Optimized**: Database queries for better performance
- ✅ **Added**: Proper error handling and user feedback
- ✅ **Improved**: Loading states and progress indicators

---

## 📋 **Usage Guide**

### **Adding Performers**

1. **From Stash Favorites**: Click "Sync from Stash" to import your existing favorites
2. **Manual Addition**: 
   - Click "Add Manually" 
   - Search for performer name
   - Select from StashDB results
   - Click "Add" to start monitoring

### **Trending Scenes**

1. **View Dashboard**: Trending scenes load automatically
2. **Refresh**: Click the refresh button to get latest trends
3. **Actions**: Click "View" to see on StashDB or "Want" to add to your list

### **Database Migration**

The migration will:
- ✅ Create backup tables (`performers_backup`, `studios_backup`)
- ✅ Update schema to make `stash_id` nullable
- ✅ Preserve all existing data
- ✅ Enable manual performer additions

---

## 🛠️ **Development**

### **Project Structure**
```
stash-filter/
├── app/
│   ├── main.py              # Main application with new API endpoints
│   ├── models.py            # Updated database models
│   ├── stashdb_api.py       # StashDB integration
│   └── ...
├── templates/
│   ├── dashboard.html       # Enhanced with trending scenes
│   ├── performers.html      # Updated with search functionality
│   └── ...
├── static/
│   ├── style.css           # New scene card styles
│   └── ...
├── migrations/
│   ├── 003_make_stash_id_nullable.py
│   └── ...
├── migrate_stash_id.py     # Migration script
├── fix_database.sh         # Automated fix script
└── README.md              # This file
```

### **API Endpoints Added**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/search-performers` | POST | Search StashDB for performers |
| `/api/add-performer` | POST | Add performer to monitoring |
| `/api/get-trending-scenes` | GET | Get trending scenes with thumbnails |

### **Building & Testing**

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python migrate_stash_id.py data/stash_filter.db

# Start development server
python -m app.main

# Run tests
python -m pytest tests/
```

---

## 🐛 **Known Issues & Solutions**

### **Issue**: "No trending scenes found"
**Solution**: Check your StashDB API key and connection in Settings

### **Issue**: Thumbnails not loading
**Solution**: Ensure your server can access external URLs (StashDB image CDN)

### **Issue**: Search returns no results
**Solution**: Verify StashDB API key and try different search terms

### **Issue**: Migration fails
**Solution**: 
1. Stop the container
2. Manually backup your database
3. Run the Python migration script directly
4. Check logs for specific error messages

---

## 📞 **Support**

If you encounter issues:

1. **Check Logs**: Look at Docker container logs for error details
2. **Database Backup**: Always backup before migration
3. **Environment**: Verify all environment variables are set correctly
4. **API Keys**: Ensure StashDB and Whisparr API keys are valid

---

## 🎯 **Coming Soon**

- 🔄 **Auto-Add Trending**: Automatically add trending scenes to wanted list
- 📊 **Scene Analytics**: Statistics on trending patterns
- 🎯 **Smart Filtering**: AI-powered scene recommendations
- 📱 **Mobile App**: Native mobile application
- 🔔 **Push Notifications**: Real-time alerts for new scenes

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- **StashDB**: For providing the excellent adult content database
- **Stash Community**: For feedback and bug reports
- **Contributors**: Everyone who helped improve this project

---

**Happy filtering! 🎉**

*For technical support, please open an issue on GitHub or check our documentation.*
