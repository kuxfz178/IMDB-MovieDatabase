import sqlite3
import pandas as pd
import os
from pathlib import Path

class IMDbDatabase:
    def __init__(self, db_path='imdb.db'):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
    
    def create_tables(self):
        """Create tables for IMDb datasets"""
        
        # Create table for title.basics.tsv (movies only)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                tconst TEXT PRIMARY KEY,
                titleType TEXT,
                primaryTitle TEXT,
                originalTitle TEXT,
                isAdult INTEGER,
                startYear INTEGER,
                endYear INTEGER,
                runtimeMinutes INTEGER,
                genres TEXT
            )
        ''')
        
        # User movie lists tables
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS want_to_watch (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_session TEXT NOT NULL,
                tconst TEXT NOT NULL,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tconst) REFERENCES movies (tconst),
                UNIQUE(user_session, tconst)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS watched_movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_session TEXT NOT NULL,
                tconst TEXT NOT NULL,
                watched_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tconst) REFERENCES movies (tconst),
                UNIQUE(user_session, tconst)
            )
        ''')
        
        self.connection.commit()
        print("Tables created successfully!")
    
    def load_title_basics(self, file_path='data/title.basics.tsv'):
        """Load title.basics.tsv into SQLite database (movies only)"""
        if not os.path.exists(file_path):
            print(f"File {file_path} not found!")
            return
        
        print(f"Loading {file_path}...")
        print("Filtering for movies only...")
        
        # Read in chunks to handle large files
        chunk_size = 10000
        chunk_count = 0
        total_movies = 0
        
        for chunk in pd.read_csv(file_path, sep='\t', na_values='\\N', chunksize=chunk_size):
            # Filter for movies only
            movies_chunk = chunk[chunk['titleType'] == 'movie'].copy()
            
            if len(movies_chunk) == 0:
                chunk_count += 1
                continue
            
            # Replace NaN with None for SQLite
            movies_chunk = movies_chunk.where(pd.notnull(movies_chunk), None)
            
            # Convert to appropriate data types
            for int_col in ['isAdult', 'startYear', 'endYear', 'runtimeMinutes']:
                if int_col in movies_chunk.columns:
                    movies_chunk[int_col] = pd.to_numeric(movies_chunk[int_col], errors='coerce')
            
            # Insert into database
            movies_chunk.to_sql('movies', self.connection, if_exists='append', index=False)
            
            total_movies += len(movies_chunk)
            chunk_count += 1
            
            if chunk_count % 10 == 0:
                print(f"Processed {chunk_count * chunk_size} rows, found {total_movies} movies so far...")
        
        print(f"Finished loading {file_path}")
        print(f"Total movies loaded: {total_movies}")
    
    def create_indexes(self):
        """Create indexes for better query performance"""
        print("Creating indexes...")
        
        # Indexes for movies table
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_movies_tconst ON movies(tconst)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_movies_primaryTitle ON movies(primaryTitle)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_movies_startYear ON movies(startYear)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_movies_genres ON movies(genres)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_movies_runtimeMinutes ON movies(runtimeMinutes)')
        
        self.connection.commit()
        print("Indexes created successfully!")
    
    def create_views(self):
        """Create database views for better data organization"""
        print("Creating database views...")
        
        # View 1: Recent high-quality movies
        self.cursor.execute('''
            CREATE VIEW IF NOT EXISTS recent_quality_movies AS
            SELECT 
                tconst,
                primaryTitle,
                startYear,
                runtimeMinutes,
                genres,
                CASE 
                    WHEN runtimeMinutes >= 120 THEN 'Long'
                    WHEN runtimeMinutes >= 90 THEN 'Standard'
                    ELSE 'Short'
                END as length_category
            FROM movies
            WHERE startYear >= 2010 
                AND runtimeMinutes >= 60
                AND isAdult = 0
                AND genres IS NOT NULL
            ORDER BY startYear DESC
        ''')
        
        # View 2: Genre statistics view
        self.cursor.execute('''
            CREATE VIEW IF NOT EXISTS genre_stats_view AS
            SELECT 
                genres,
                COUNT(*) as movie_count,
                AVG(runtimeMinutes) as avg_runtime,
                MIN(startYear) as earliest_year,
                MAX(startYear) as latest_year
            FROM movies
            WHERE genres IS NOT NULL 
                AND runtimeMinutes IS NOT NULL
            GROUP BY genres
            HAVING movie_count >= 5
            ORDER BY movie_count DESC
        ''')
        
        # View 3: Decade summary view
        self.cursor.execute('''
            CREATE VIEW IF NOT EXISTS decade_summary AS
            SELECT 
                (startYear / 10) * 10 as decade,
                COUNT(*) as total_movies,
                AVG(runtimeMinutes) as avg_runtime,
                COUNT(CASE WHEN isAdult = 0 THEN 1 END) as family_friendly,
                COUNT(CASE WHEN isAdult = 1 THEN 1 END) as adult_movies
            FROM movies
            WHERE startYear IS NOT NULL AND startYear >= 1920
            GROUP BY decade
            ORDER BY decade DESC
        ''')
        
        self.connection.commit()
        print("Database views created successfully!")
    
    def get_table_info(self, table_name):
        """Get information about a table"""
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        return self.cursor.fetchall()
    
    def get_row_count(self, table_name):
        """Get the number of rows in a table"""
        self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        return self.cursor.fetchone()[0]
    
    def close(self):
        """Close database connection"""
        self.connection.close()

def main():
    """Main function to set up the database"""
    print("Setting up IMDb Movies database...")
    
    # Initialize database
    db = IMDbDatabase()
    
    # Create tables
    db.create_tables()
    
    # Load data
    print("\nLoading movie data...")
    db.load_title_basics()
    
    # Create indexes for better performance
    db.create_indexes()
    
    # Create database views
    print("\nCreating database views...")
    db.create_views()
    
    # Show summary
    print("\nDatabase setup complete!")
    print(f"Movies loaded: {db.get_row_count('movies'):,}")
    
    # Show some sample statistics
    cursor = db.cursor
    cursor.execute("SELECT COUNT(*) FROM movies WHERE startYear >= 2020")
    recent_movies = cursor.fetchone()[0]
    print(f"Movies from 2020 onwards: {recent_movies:,}")
    
    cursor.execute("SELECT COUNT(DISTINCT genres) FROM movies WHERE genres IS NOT NULL")
    genre_combinations = cursor.fetchone()[0]
    print(f"Unique genre combinations: {genre_combinations:,}")
    
    db.close()

if __name__ == "__main__":
    main() 