import sqlite3
import hashlib
import os

DB_PATH = "users.db"

def init_db():
    """Initialize the users database"""
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE users
                    (id INTEGER PRIMARY KEY,
                     username TEXT UNIQUE NOT NULL,
                     password TEXT NOT NULL,
                     email TEXT UNIQUE NOT NULL,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()

def hash_password(password):
    """Hash a password for security"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, email, password):
    """Register a new user
    Returns: (success: bool, message: str)
    """
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Check if username already exists
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        if c.fetchone():
            return False, "Username already exists. Please choose a different one."
        
        # Check if email already exists
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        if c.fetchone():
            return False, "Email already registered. Please use a different email."
        
        # Validate password length
        if len(password) < 6:
            return False, "Password must be at least 6 characters long."
        
        # Insert new user
        hashed_pw = hash_password(password)
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                 (username, email, hashed_pw))
        conn.commit()
        conn.close()
        
        return True, "Registration successful! You can now login."
    except Exception as e:
        return False, f"Registration error: {str(e)}"

def login_user(username, password):
    """Login a user
    Returns: (success: bool, message: str, user_data: dict or None)
    """
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        hashed_pw = hash_password(password)
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?",
                 (username, hashed_pw))
        user = c.fetchone()
        conn.close()
        
        if user:
            user_data = {
                'id': user[0],
                'username': user[1],
                'email': user[3]
            }
            return True, "Login successful!", user_data
        else:
            return False, "Invalid username or password.", None
    except Exception as e:
        return False, f"Login error: {str(e)}", None

def get_user_data(username):
    """Get user data by username"""
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("SELECT id, username, email FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'email': user[2]
            }
        return None
    except Exception as e:
        print(f"Error getting user data: {str(e)}")
        return None
