#!/usr/bin/env python3
"""
Add user movie list tables to existing IMDb database
"""

import sqlite3
import os

def add_user_tables():
    """Add user movie list tables to existing database"""
    if not os.path.exists('imdb.db'):
        print("Database 'imdb.db' not found! Please run database_setup.py first.")
        return False
    
    print("Adding user movie list tables to existing database...")
    
    conn = sqlite3.connect('imdb.db')
    cursor = conn.cursor()
    
    try:
        # Create want_to_watch table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS want_to_watch (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_session TEXT NOT NULL,
                tconst TEXT NOT NULL,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tconst) REFERENCES movies (tconst),
                UNIQUE(user_session, tconst)
            )
        ''')
        
        # Create watched_movies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watched_movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_session TEXT NOT NULL,
                tconst TEXT NOT NULL,
                watched_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tconst) REFERENCES movies (tconst),
                UNIQUE(user_session, tconst)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_want_to_watch_user_session ON want_to_watch(user_session)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_want_to_watch_tconst ON want_to_watch(tconst)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_watched_movies_user_session ON watched_movies(user_session)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_watched_movies_tconst ON watched_movies(tconst)')
        
        conn.commit()
        print("✅ User movie list tables added successfully!")
        
        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('want_to_watch', 'watched_movies')")
        tables = cursor.fetchall()
        print(f"Created tables: {[table[0] for table in tables]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding user tables: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    add_user_tables() 