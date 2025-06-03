import sqlite3
import pandas as pd
import re
from typing import List, Dict, Any, Optional

class IMDbQueries:
    def __init__(self, db_path='imdb.db'):
        self.db_path = db_path
    
    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def get_sample_movies(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get sample movies"""
        with self._get_connection() as conn:
            query = """
                SELECT tconst, primaryTitle, originalTitle, startYear, runtimeMinutes, genres
                FROM movies 
                WHERE primaryTitle IS NOT NULL AND (startYear IS NULL OR startYear <= 2025)
                LIMIT ?
            """
            cursor = conn.cursor()
            cursor.execute(query, (limit,))
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    
    def get_movies_by_year(self, year: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get movies by release year"""
        with self._get_connection() as conn:
            query = """
                SELECT tconst, primaryTitle, originalTitle, runtimeMinutes, genres
                FROM movies 
                WHERE startYear = ? AND primaryTitle IS NOT NULL
                ORDER BY primaryTitle
                LIMIT ?
            """
            cursor = conn.cursor()
            cursor.execute(query, (year, limit))
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    
    def get_movies_by_year_range(self, start_year: int, end_year: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get movies within a year range"""
        with self._get_connection() as conn:
            query = """
                SELECT tconst, primaryTitle, originalTitle, startYear, runtimeMinutes, genres
                FROM movies 
                WHERE startYear BETWEEN ? AND ? AND primaryTitle IS NOT NULL
                ORDER BY startYear DESC, primaryTitle
                LIMIT ?
            """
            cursor = conn.cursor()
            cursor.execute(query, (start_year, end_year, limit))
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    
    def search_movies(self, search_term: str, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Search for movies by title with exact matches first"""
        with self._get_connection() as conn:
            query = """
                SELECT tconst, primaryTitle, originalTitle, startYear, runtimeMinutes, genres,
                    -- Ranking for search relevance (lower number = higher priority)
                    CASE 
                        WHEN LOWER(primaryTitle) = LOWER(?) THEN 1
                        WHEN LOWER(originalTitle) = LOWER(?) THEN 1
                        WHEN LOWER(primaryTitle) LIKE LOWER(?) THEN 2
                        WHEN LOWER(originalTitle) LIKE LOWER(?) THEN 2
                        WHEN LOWER(primaryTitle) LIKE LOWER(?) THEN 3
                        WHEN LOWER(originalTitle) LIKE LOWER(?) THEN 3
                        ELSE 4
                    END as search_rank
                FROM movies 
                WHERE (LOWER(primaryTitle) LIKE LOWER(?) OR LOWER(originalTitle) LIKE LOWER(?)) 
                    AND primaryTitle IS NOT NULL 
                    AND (startYear IS NULL OR startYear <= 2025)
                ORDER BY search_rank ASC, startYear DESC
                LIMIT ? OFFSET ?
            """
            
            # Prepare search patterns
            exact_match = search_term
            starts_with = f"{search_term}%"
            contains = f"%{search_term}%"
            
            cursor = conn.cursor()
            cursor.execute(query, (
                exact_match, exact_match,           # Exact match check
                starts_with, starts_with,           # Starts with check  
                contains, contains,                 # Contains check
                contains, contains,                 # WHERE clause
                limit, offset
            ))
            
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            # Remove the search_rank column from results
            filtered_columns = [col for col in columns if col != 'search_rank']
            filtered_rows = []
            for row in rows:
                filtered_row = []
                for i, col in enumerate(columns):
                    if col != 'search_rank':
                        filtered_row.append(row[i])
                filtered_rows.append(tuple(filtered_row))
            
            return [dict(zip(filtered_columns, row)) for row in filtered_rows]
    
    def get_movies_by_genre(self, genre: str, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Get movies by genre"""
        with self._get_connection() as conn:
            query = """
                SELECT tconst, primaryTitle, originalTitle, startYear, runtimeMinutes, genres
                FROM movies 
                WHERE genres LIKE ? 
                    AND primaryTitle IS NOT NULL 
                    AND (startYear IS NULL OR startYear <= 2025)
                ORDER BY startYear DESC
                LIMIT ? OFFSET ?
            """
            genre_pattern = f"%{genre}%"
            cursor = conn.cursor()
            cursor.execute(query, (genre_pattern, limit, offset))
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    
    def get_movies_by_runtime(self, min_runtime: int, max_runtime: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get movies by runtime range"""
        with self._get_connection() as conn:
            query = """
                SELECT tconst, primaryTitle, originalTitle, startYear, runtimeMinutes, genres
                FROM movies 
                WHERE runtimeMinutes BETWEEN ? AND ? AND primaryTitle IS NOT NULL
                ORDER BY runtimeMinutes DESC
                LIMIT ?
            """
            cursor = conn.cursor()
            cursor.execute(query, (min_runtime, max_runtime, limit))
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    
    def get_longest_movies(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the longest movies"""
        with self._get_connection() as conn:
            query = """
                SELECT tconst, primaryTitle, originalTitle, startYear, runtimeMinutes, genres
                FROM movies 
                WHERE runtimeMinutes IS NOT NULL AND primaryTitle IS NOT NULL
                ORDER BY runtimeMinutes DESC
                LIMIT ?
            """
            cursor = conn.cursor()
            cursor.execute(query, (limit,))
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    
    def get_recent_movies(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Get the most recent movies"""
        with self._get_connection() as conn:
            query = """
                SELECT tconst, primaryTitle, originalTitle, startYear, runtimeMinutes, genres
                FROM movies 
                WHERE startYear IS NOT NULL 
                    AND primaryTitle IS NOT NULL 
                    AND startYear <= 2025
                ORDER BY startYear DESC, primaryTitle
                LIMIT ? OFFSET ?
            """
            cursor = conn.cursor()
            cursor.execute(query, (limit, offset))
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    
    def get_movies_stats_by_year(self) -> List[Dict[str, Any]]:
        """Get movie count statistics by year"""
        with self._get_connection() as conn:
            query = """
                SELECT startYear, COUNT(*) as movie_count
                FROM movies 
                WHERE startYear IS NOT NULL AND startYear >= 1900
                GROUP BY startYear
                ORDER BY startYear DESC
                LIMIT 30
            """
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    
    def get_genre_stats(self) -> List[Dict[str, Any]]:
        """Get statistics by genre combinations"""
        with self._get_connection() as conn:
            query = """
                SELECT genres, COUNT(*) as movie_count
                FROM movies 
                WHERE genres IS NOT NULL
                GROUP BY genres
                ORDER BY movie_count DESC
                LIMIT 20
            """
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    
    def get_runtime_stats(self) -> Dict[str, Any]:
        """Get runtime statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Average runtime
            cursor.execute("SELECT AVG(runtimeMinutes) FROM movies WHERE runtimeMinutes IS NOT NULL")
            avg_runtime = cursor.fetchone()[0]
            
            # Min runtime
            cursor.execute("SELECT MIN(runtimeMinutes) FROM movies WHERE runtimeMinutes IS NOT NULL")
            min_runtime = cursor.fetchone()[0]
            
            # Max runtime
            cursor.execute("SELECT MAX(runtimeMinutes) FROM movies WHERE runtimeMinutes IS NOT NULL")
            max_runtime = cursor.fetchone()[0]
            
            # Movies with runtime data
            cursor.execute("SELECT COUNT(*) FROM movies WHERE runtimeMinutes IS NOT NULL")
            movies_with_runtime = cursor.fetchone()[0]
            
            return {
                'average_runtime_minutes': round(avg_runtime, 2) if avg_runtime else None,
                'min_runtime_minutes': min_runtime,
                'max_runtime_minutes': max_runtime,
                'movies_with_runtime_data': movies_with_runtime
            }
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get overall database statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get total movie count
            cursor.execute("SELECT COUNT(*) FROM movies")
            total_movies = cursor.fetchone()[0]
            
            # Get movies with non-null start year
            cursor.execute("SELECT COUNT(*) FROM movies WHERE startYear IS NOT NULL")
            movies_with_year = cursor.fetchone()[0]
            
            # Get year range
            cursor.execute("SELECT MIN(startYear), MAX(startYear) FROM movies WHERE startYear IS NOT NULL")
            year_range = cursor.fetchone()
            min_year, max_year = year_range if year_range else (None, None)
            
            # Get unique genres count
            cursor.execute("SELECT COUNT(DISTINCT genres) FROM movies WHERE genres IS NOT NULL")
            unique_genres = cursor.fetchone()[0]
            
            # Get adult vs non-adult counts
            cursor.execute("SELECT COUNT(*) FROM movies WHERE isAdult = 1")
            adult_movies = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM movies WHERE isAdult = 0")
            non_adult_movies = cursor.fetchone()[0]
            
            return {
                'total_movies': total_movies,
                'movies_with_year': movies_with_year,
                'year_range': f"{min_year}-{max_year}" if min_year and max_year else None,
                'unique_genre_combinations': unique_genres,
                'adult_movies': adult_movies,
                'non_adult_movies': non_adult_movies
            }
    
    def get_recommendations(self, want_to_watch_movie_ids: List[str], watched_movie_ids: List[str] = None, limit: int = 15) -> Dict[str, Any]:
        """Get movie recommendations based on want to watch and watched movies"""
        if watched_movie_ids is None:
            watched_movie_ids = []
            
        # Combine both lists for preference analysis
        all_interaction_ids = want_to_watch_movie_ids + watched_movie_ids
        total_interactions = len(all_interaction_ids)
        
        if total_interactions < 5:
            return {
                'recommendations': [],
                'analysis': {
                    'top_genres': [],
                    'preferred_years': 'Unknown',
                    'avg_runtime': None,
                    'total_interactions': total_interactions,
                    'error': f'Need at least 5 movie interactions (current: {total_interactions})'
                }
            }
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Convert all movie IDs to a comma-separated string for SQL
            all_ids_str = "','".join(all_interaction_ids)
            
            # Analyze all interacted movies to understand preferences
            analysis_query = f"""
                SELECT genres, startYear, runtimeMinutes
                FROM movies 
                WHERE tconst IN ('{all_ids_str}') 
                AND genres IS NOT NULL
            """
            
            cursor.execute(analysis_query)
            interaction_movies_data = cursor.fetchall()
            
            if not interaction_movies_data:
                return {
                    'recommendations': [],
                    'analysis': {
                        'top_genres': [],
                        'preferred_years': 'Unknown',
                        'avg_runtime': None,
                        'total_interactions': total_interactions,
                        'error': 'No genre data found for selected movies'
                    }
                }
            
            # Analyze genre preferences from all interactions
            all_genres = []
            years = []
            runtimes = []
            
            for genres, year, runtime in interaction_movies_data:
                if genres:
                    # Split comma-separated genres and add to list
                    movie_genres = [g.strip() for g in genres.split(',')]
                    all_genres.extend(movie_genres)
                if year:
                    years.append(year)
                if runtime:
                    runtimes.append(runtime)
            
            # Count genre frequencies
            from collections import Counter
            genre_counts = Counter(all_genres)
            top_genres = [genre for genre, count in genre_counts.most_common(5)]
            
            if not top_genres:
                return {
                    'recommendations': [],
                    'analysis': {
                        'top_genres': [],
                        'preferred_years': 'Unknown',
                        'avg_runtime': None,
                        'total_interactions': total_interactions,
                        'error': 'No genres found in selected movies'
                    }
                }
            
            # Calculate preferred year range and average runtime
            avg_year = sum(years) / len(years) if years else 2020
            avg_runtime = sum(runtimes) / len(runtimes) if runtimes else None
            
            # Build genre conditions for SQL
            genre_conditions = []
            for genre in top_genres[:3]:  # Use top 3 genres
                genre_conditions.append(f"genres LIKE '%{genre}%'")
            
            genre_where_clause = " OR ".join(genre_conditions) if genre_conditions else "1=1"
            
            # Build recommendation query
            recommendation_query = f"""
                SELECT 
                    tconst, primaryTitle, originalTitle, startYear, runtimeMinutes, genres,
                    -- Score based on genre overlap, year proximity, and runtime similarity
                    (CASE 
                        WHEN genres IS NULL THEN 0
                        ELSE (
                            -- Genre similarity score (count matching genres)
                            {' + '.join([f"(CASE WHEN genres LIKE '%{genre}%' THEN 3 ELSE 0 END)" for genre in top_genres[:3]])}
                            -- Year proximity bonus (closer to average preferred year)
                            + (CASE WHEN startYear IS NOT NULL THEN 
                                MAX(0, 5 - ABS(startYear - {avg_year}) / 10) 
                              ELSE 0 END)
                            -- Runtime similarity bonus (if we have runtime preference)
                            {f"+ (CASE WHEN runtimeMinutes IS NOT NULL THEN MAX(0, 3 - ABS(runtimeMinutes - {avg_runtime}) / 30) ELSE 0 END)" if avg_runtime else "+ 0"}
                            -- Recent movie bonus
                            + (CASE WHEN startYear >= 2010 THEN 2 ELSE 0 END)
                            -- Quality proxy: reasonable runtime
                            + (CASE WHEN runtimeMinutes >= 80 AND runtimeMinutes <= 180 THEN 1 ELSE 0 END)
                        )
                    END) as recommendation_score
                FROM movies 
                WHERE tconst NOT IN ('{all_ids_str}')
                    AND primaryTitle IS NOT NULL 
                    AND genres IS NOT NULL
                    AND isAdult = 0
                    AND (startYear IS NULL OR startYear <= 2025)
                    AND startYear >= 1970
                    -- Must have at least one matching genre
                    AND ({genre_where_clause})
                ORDER BY recommendation_score DESC, startYear DESC
                LIMIT ?
            """
            
            try:
                cursor.execute(recommendation_query, (limit,))
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries, excluding the score column
                recommendations = []
                for row in rows:
                    movie_dict = dict(zip(columns, row))
                    # Remove the score from the returned data
                    movie_dict.pop('recommendation_score', None)
                    recommendations.append(movie_dict)
                
                return {
                    'recommendations': recommendations,
                    'analysis': {
                        'top_genres': top_genres,
                        'preferred_years': f"{min(years)}-{max(years)}" if years else "Unknown",
                        'avg_runtime': round(avg_runtime, 1) if avg_runtime else None,
                        'total_interactions': total_interactions,
                        'want_to_watch_count': len(want_to_watch_movie_ids),
                        'watched_count': len(watched_movie_ids)
                    }
                }
            except Exception as e:
                return {
                    'recommendations': [],
                    'analysis': {
                        'top_genres': top_genres,
                        'preferred_years': 'Unknown',
                        'avg_runtime': None,
                        'total_interactions': total_interactions,
                        'error': f'Database query error: {str(e)}'
                    }
                }

    def advanced_search(self, search_term: str, search_type: str = "basic", limit: int = 10) -> List[Dict[str, Any]]:
        """Advanced search with regex support and pattern matching"""
        with self._get_connection() as conn:
            
            if search_type == "regex":
                # Use Python regex for advanced pattern matching
                # First get all movies, then filter with regex (for demonstration)
                query = """
                    SELECT tconst, primaryTitle, originalTitle, startYear, runtimeMinutes, genres
                    FROM movies 
                    WHERE primaryTitle IS NOT NULL
                    LIMIT 1000
                """
                cursor = conn.cursor()
                cursor.execute(query)
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                
                # Apply regex filtering in Python
                try:
                    pattern = re.compile(search_term, re.IGNORECASE)
                    filtered_rows = []
                    
                    for row in rows:
                        title = row[1]  # primaryTitle
                        original_title = row[2]  # originalTitle
                        
                        if (title and pattern.search(title)) or (original_title and pattern.search(original_title)):
                            filtered_rows.append(row)
                            if len(filtered_rows) >= limit:
                                break
                    
                    return [dict(zip(columns, row)) for row in filtered_rows]
                except re.error:
                    # Fall back to basic search if regex is invalid
                    return self.search_movies(search_term, limit)
            
            elif search_type == "year_pattern":
                # Pattern matching for years (e.g., "199*" for 1990s)
                year_pattern = search_term.replace('*', '%')
                query = """
                    SELECT tconst, primaryTitle, originalTitle, startYear, runtimeMinutes, genres
                    FROM movies 
                    WHERE CAST(startYear AS TEXT) LIKE ? AND primaryTitle IS NOT NULL
                    ORDER BY startYear DESC
                    LIMIT ?
                """
                cursor = conn.cursor()
                cursor.execute(query, (year_pattern, limit))
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
            
            elif search_type == "genre_pattern":
                # Advanced genre pattern matching
                # Support patterns like "Action+Comedy" (both), "Action|Comedy" (either)
                if '+' in search_term:
                    # Must have ALL genres
                    genres = [g.strip() for g in search_term.split('+')]
                    conditions = " AND ".join([f"genres LIKE '%{genre}%'" for genre in genres])
                    query = f"""
                        SELECT tconst, primaryTitle, originalTitle, startYear, runtimeMinutes, genres
                        FROM movies 
                        WHERE {conditions} AND primaryTitle IS NOT NULL
                        ORDER BY startYear DESC
                        LIMIT ?
                    """
                elif '|' in search_term:
                    # Must have ANY genre
                    genres = [g.strip() for g in search_term.split('|')]
                    conditions = " OR ".join([f"genres LIKE '%{genre}%'" for genre in genres])
                    query = f"""
                        SELECT tconst, primaryTitle, originalTitle, startYear, runtimeMinutes, genres
                        FROM movies 
                        WHERE ({conditions}) AND primaryTitle IS NOT NULL
                        ORDER BY startYear DESC
                        LIMIT ?
                    """
                else:
                    # Single genre
                    query = """
                        SELECT tconst, primaryTitle, originalTitle, startYear, runtimeMinutes, genres
                        FROM movies 
                        WHERE genres LIKE ? AND primaryTitle IS NOT NULL
                        ORDER BY startYear DESC
                        LIMIT ?
                    """
                    search_term = f"%{search_term}%"
                
                cursor = conn.cursor()
                if '+' in search_term or '|' in search_term:
                    cursor.execute(query, (limit,))
                else:
                    cursor.execute(query, (search_term, limit))
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
            
            else:
                # Default to basic search
                return self.search_movies(search_term, limit)

    def create_database_views(self):
        """Create database views for better data organization"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # View 1: Recent high-quality movies
            cursor.execute('''
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
            cursor.execute('''
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
            cursor.execute('''
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
            
            conn.commit()
            print("Database views created successfully!")

    def get_view_data(self, view_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get data from a specific database view"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Validate view name for security
            valid_views = ['recent_quality_movies', 'genre_stats_view', 'decade_summary']
            if view_name not in valid_views:
                raise ValueError(f"Invalid view name. Must be one of: {valid_views}")
            
            query = f"SELECT * FROM {view_name} LIMIT ?"
            cursor.execute(query, (limit,))
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]

    def regex_title_search(self, pattern: str, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Search movie titles using regular expressions"""
        with self._get_connection() as conn:
            # Get movies and apply regex in Python (SQLite doesn't have built-in regex)
            query = """
                SELECT tconst, primaryTitle, originalTitle, startYear, runtimeMinutes, genres
                FROM movies 
                WHERE primaryTitle IS NOT NULL 
                    AND (startYear IS NULL OR startYear <= 2025)
                ORDER BY startYear DESC
            """
            
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [description[0] for description in cursor.description]
            
            try:
                regex_pattern = re.compile(pattern, re.IGNORECASE)
                matching_movies = []
                skip_count = 0
                
                for row in cursor.fetchall():
                    title = row[1]  # primaryTitle
                    original_title = row[2]  # originalTitle
                    
                    # Test both titles against the regex
                    if ((title and regex_pattern.search(title)) or 
                        (original_title and regex_pattern.search(original_title))):
                        
                        # Handle offset
                        if skip_count < offset:
                            skip_count += 1
                            continue
                            
                        matching_movies.append(dict(zip(columns, row)))
                        
                        if len(matching_movies) >= limit:
                            break
                
                return matching_movies
                
            except re.error as e:
                raise ValueError(f"Invalid regular expression: {e}")

    # User Movie Lists Management
    def add_to_want_to_watch(self, user_session: str, tconst: str) -> bool:
        """Add a movie to user's want to watch list"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO want_to_watch (user_session, tconst) VALUES (?, ?)",
                    (user_session, tconst)
                )
                conn.commit()
                return cursor.rowcount > 0
            except Exception as e:
                print(f"Error adding to want to watch: {e}")
                return False

    def remove_from_want_to_watch(self, user_session: str, tconst: str) -> bool:
        """Remove a movie from user's want to watch list"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "DELETE FROM want_to_watch WHERE user_session = ? AND tconst = ?",
                    (user_session, tconst)
                )
                conn.commit()
                return cursor.rowcount > 0
            except Exception as e:
                print(f"Error removing from want to watch: {e}")
                return False

    def get_want_to_watch_movies(self, user_session: str) -> List[Dict[str, Any]]:
        """Get user's want to watch movies"""
        with self._get_connection() as conn:
            query = """
                SELECT m.tconst, m.primaryTitle, m.originalTitle, m.startYear, 
                       m.runtimeMinutes, m.genres, w.added_date
                FROM want_to_watch w
                JOIN movies m ON w.tconst = m.tconst
                WHERE w.user_session = ?
                ORDER BY w.added_date DESC
            """
            cursor = conn.cursor()
            cursor.execute(query, (user_session,))
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]

    def add_to_watched(self, user_session: str, tconst: str) -> bool:
        """Add a movie to user's watched list"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO watched_movies (user_session, tconst) VALUES (?, ?)",
                    (user_session, tconst)
                )
                conn.commit()
                return cursor.rowcount > 0
            except Exception as e:
                print(f"Error adding to watched: {e}")
                return False

    def remove_from_watched(self, user_session: str, tconst: str) -> bool:
        """Remove a movie from user's watched list"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "DELETE FROM watched_movies WHERE user_session = ? AND tconst = ?",
                    (user_session, tconst)
                )
                conn.commit()
                return cursor.rowcount > 0
            except Exception as e:
                print(f"Error removing from watched: {e}")
                return False

    def get_watched_movies(self, user_session: str) -> List[Dict[str, Any]]:
        """Get user's watched movies"""
        with self._get_connection() as conn:
            query = """
                SELECT m.tconst, m.primaryTitle, m.originalTitle, m.startYear, 
                       m.runtimeMinutes, m.genres, w.watched_date
                FROM watched_movies w
                JOIN movies m ON w.tconst = m.tconst
                WHERE w.user_session = ?
                ORDER BY w.watched_date DESC
            """
            cursor = conn.cursor()
            cursor.execute(query, (user_session,))
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]

    def clear_want_to_watch(self, user_session: str) -> bool:
        """Clear all movies from user's want to watch list"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM want_to_watch WHERE user_session = ?", (user_session,))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error clearing want to watch: {e}")
                return False

    def clear_watched(self, user_session: str) -> bool:
        """Clear all movies from user's watched list"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM watched_movies WHERE user_session = ?", (user_session,))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error clearing watched: {e}")
                return False

    def get_user_movie_lists_summary(self, user_session: str) -> Dict[str, Any]:
        """Get summary of user's movie lists"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Count want to watch movies
            cursor.execute("SELECT COUNT(*) FROM want_to_watch WHERE user_session = ?", (user_session,))
            want_to_watch_count = cursor.fetchone()[0]
            
            # Count watched movies
            cursor.execute("SELECT COUNT(*) FROM watched_movies WHERE user_session = ?", (user_session,))
            watched_count = cursor.fetchone()[0]
            
            return {
                'want_to_watch_count': want_to_watch_count,
                'watched_count': watched_count,
                'total_interactions': want_to_watch_count + watched_count
            } 