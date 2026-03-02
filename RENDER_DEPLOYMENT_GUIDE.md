# Deploy Flask App on Render - Complete Guide

## Step 1: Prepare Your Project for Deployment

### 1.1 File Structure Check
Ensure your project has this structure:
```
d:/LFP-BOX/
├── app.py              # Main Flask application
├── requirements.txt    # Dependencies
├── templates/
│   └── index.html     # Frontend HTML
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── app.js
├── models/
│   └── database.py
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   ├── items.py
│   └── admin.py
└── campus_lost_found.db  # SQLite database (will be created)
```

### 1.2 Update requirements.txt
```
txt
Flask==3.0.0
flask-cors==4.0.0
PyJWT==2.8.0
bcrypt==4.1.2
gunicorn==21.2.0
```

### 1.3 Update app.py for Production
Make these changes to `app.py`:

```
python
# Add this at the top
import os

# Change the database path for production
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'campus_lost_found.db')

# Update the last section:
if __name__ == '__main__':
    # Initialize database
    print("Initializing database...")
    init_database()
    
    # Get port from environment (Render provides this)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the Flask app
    print(f"Starting CampusLost API server on port {port}...")
    app.run(host='0.0.0.0', port=port)
```

---

## Step 2: GitHub Setup

### 2.1 Create GitHub Repository
1. Go to github.com and create a new repository
2. Name it: `campus-lost-found`

### 2.2 Push Your Code
```
bash
# In your project folder
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/campus-lost-found.git
git push -u origin main
```

---

## Step 3: Deploy on Render

### 3.1 Create Render Account
1. Go to render.com
2. Sign up with GitHub

### 3.2 Create Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: campus-lost-found
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free (select)

### 3.3 Environment Variables
Render automatically sets `PORT` variable. No extra setup needed.

### 3.4 Deploy
Click "Create Web Service" and wait for deployment (2-5 minutes).

---

## Step 4: SQLite on Render

### 4.1 How It Works
- SQLite file is created automatically on first run
- Database persists in the server's filesystem
- Data survives deployments (but NOT server restarts)

### 4.2 Important Notes
- Free tier: Server sleeps after 15 min inactivity
- On wake: Database resets if server was hibernating
- For persistent data: Use Render's PostgreSQL (see below)

---

## Step 5: Optional - Use PostgreSQL (Recommended for Production)

### 5.1 Create PostgreSQL Database
1. In Render dashboard: New → PostgreSQL
2. Configure:
   - **Name**: campus-lost-found-db
   - **User**: (auto-generated)
   - **Plan**: Free

### 5.2 Update database.py
```
python
# For PostgreSQL (optional)
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Get database URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    """Create and return a database connection"""
    try:
        if DATABASE_URL:
            # Use PostgreSQL
            conn = psycopg2.connect(DATABASE_URL)
            conn.row_factory = RealDictCursor
            return conn
        else:
            # Use SQLite (for local development)
            connection = sqlite3.connect(DB_PATH)
            connection.row_factory = sqlite3.Row
            return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None
```

---

## Step 6: Testing Your Deployment

### 6.1 Test the API
After deployment, test:
```
https://your-app-name.onrender.com/api/health
```

Expected response:
```
json
{"status": "ok", "message": "CampusLost API is running"}
```

### 6.2 Test the Frontend
```
https://your-app-name.onrender.com/
```

---

## Common Errors and Fixes

### Error 1: "Application failed to start"
- **Cause**: Missing dependencies
- **Fix**: Check requirements.txt has all packages

### Error 2: "Database connection failed"
- **Cause**: SQLite file not created
- **Fix**: First request triggers database creation

### Error 3: "ModuleNotFoundError"
- **Cause**: Wrong folder structure
- **Fix**: Ensure app.py is in root, not in subfolder

### Error 4: "Static files not loading"
- **Cause**: Wrong static folder path
- **Fix**: Use `url_for('static', filename='css/styles.css')`

### Error 5: "Port binding error"
- **Cause**: Hardcoded port
- **Fix**: Use `os.environ.get('PORT', 5000)`

---

## Quick Commands Reference

```
bash
# Local development
pip install -r requirements.txt
python app.py

# Test production locally
gunicorn app:app

# Push to GitHub
git add .
git commit -m "Update"
git push origin main
```

---

## Your Render URL Will Be:
```
https://campus-lost-found.onrender.com
```

(Replace "campus-lost-found" with your service name)
