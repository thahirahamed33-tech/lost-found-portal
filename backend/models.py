# Database configuration and initialization (SQLite)
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'campus_lost_found.db')

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = sqlite3.connect(DB_PATH)
        connection.row_factory = sqlite3.Row
        return connection
    except Exception as e:
        print(f"Error connecting to SQLite: {e}")
        return None

def init_database():
    """Initialize the database and create tables if they don't exist"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                location TEXT,
                date TEXT,
                image TEXT,
                user_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Claims table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS claims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                proof TEXT NOT NULL,
                contact TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Notifications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                message TEXT NOT NULL,
                read_status INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        connection.commit()
        
        # Create default admin user if not exists
        cursor.execute("SELECT id FROM users WHERE email = ?", ('admin@campus.edu',))
        if not cursor.fetchone():
            import bcrypt
            hashed = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("""
                INSERT INTO users (name, email, phone, password, role)
                VALUES (?, ?, ?, ?, ?)
            """, ('Admin User', 'admin@campus.edu', '+1 555 100 0001', hashed.decode('utf-8'), 'admin'))
            print("Default admin user created")
        
        # Create default user if not exists
        cursor.execute("SELECT id FROM users WHERE email = ?", ('user@college.edu',))
        if not cursor.fetchone():
            import bcrypt
            hashed = bcrypt.hashpw('user123'.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("""
                INSERT INTO users (name, email, phone, password, role)
                VALUES (?, ?, ?, ?, ?)
            """, ('Test User', 'user@college.edu', '+1 555 123 4567', hashed.decode('utf-8'), 'user'))
            print("Default test user created")
        
        connection.commit()
        cursor.close()
        connection.close()
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
