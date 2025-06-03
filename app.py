from flask import Flask, jsonify, request, render_template_string, session
from imdb_queries import IMDbQueries
import os
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'imdb-movies-secret-key-change-in-production')
queries = IMDbQueries()

def get_user_session():
    """Get or create a user session ID"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return session['user_id']

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IMDb Movies Database</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .endpoint {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
        }
        .endpoint h3 {
            color: #495057;
        }
        .method {
            background: #007bff;
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
        }
        .url {
            font-family: monospace;
            background: #e9ecef;
            padding: 5px 10px;
            border-radius: 3px;
            margin: 5px 0;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-card {
            background: #e3f2fd;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #1976d2;
        }
        .btn {
            background: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 5px;
        }
        .btn:hover {
            background: #0056b3;
        }
        .btn-danger:hover {
            background: #bd2130;
        }
        .btn-large {
            padding: 15px 30px;
            font-size: 16px;
            font-weight: bold;
        }
        .btn-info {
            background: #17a2b8;
        }
        .btn-info:hover {
            background: #138496;
        }
        .btn-secondary {
            background: #6c757d;
        }
        .btn-secondary:hover {
            background: #545b62;
        }
        .want-to-watch-movie {
            border-color: #28a745;
            background: #f8fff9;
        }
        .watched-movie {
            border-color: #17a2b8;
            background: #f0f9ff;
        }
        .movie-item.want-to-watch-movie.watched-movie {
            border-color: #6f42c1;
            background: #f8f9ff;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎬 IMDb Movies Database</h1>
        <p>RESTful API for exploring movie data from IMDb</p>
        <a href="/dashboard" class="btn" style="margin-top: 15px;">Go to Dashboard</a>
    </div>

    <div class="container">
        <h2>Database Statistics</h2>
        <div class="stats" id="stats">
            Loading statistics...
        </div>
    </div>

    <div class="container">
        <h2>Available Endpoints</h2>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> Database Statistics</h3>
            <div class="url">/api/stats</div>
            <p>Get overall database statistics including movie counts and coverage.</p>
            <a href="/api/stats" class="btn">Try it</a>
        </div>

        <div class="endpoint">
            <h3><span class="method">GET</span> Sample Movies</h3>
            <div class="url">/api/movies?limit=10</div>
            <p>Get sample movies from the database.</p>
            <a href="/api/movies?limit=10" class="btn">Try it</a>
        </div>

        <div class="endpoint">
            <h3><span class="method">GET</span> Movies by Year</h3>
            <div class="url">/api/movies/year/2023?limit=10</div>
            <p>Get movies released in a specific year.</p>
            <a href="/api/movies/year/2023?limit=10" class="btn">2023 Movies</a>
            <a href="/api/movies/year/2020?limit=10" class="btn">2020 Movies</a>
        </div>

        <div class="endpoint">
            <h3><span class="method">GET</span> Movies by Year Range</h3>
            <div class="url">/api/movies/years/2020/2023?limit=10</div>
            <p>Get movies released within a year range.</p>
            <a href="/api/movies/years/2020/2023?limit=10" class="btn">2020-2023</a>
            <a href="/api/movies/years/2010/2015?limit=10" class="btn">2010-2015</a>
        </div>

        <div class="endpoint">
            <h3><span class="method">GET</span> Search Movies</h3>
            <div class="url">/api/movies/search?q=batman&limit=10</div>
            <p>Search for movies by title (both primary and original titles).</p>
            <a href="/api/movies/search?q=batman&limit=10" class="btn">Search Batman</a>
            <a href="/api/movies/search?q=star&limit=10" class="btn">Search Star</a>
        </div>

        <div class="endpoint">
            <h3><span class="method">GET</span> Movies by Genre</h3>
            <div class="url">/api/movies/genre/Action?limit=10</div>
            <p>Get movies by genre (Action, Comedy, Drama, etc.).</p>
            <a href="/api/movies/genre/Action?limit=10" class="btn">Action</a>
            <a href="/api/movies/genre/Comedy?limit=10" class="btn">Comedy</a>
            <a href="/api/movies/genre/Drama?limit=10" class="btn">Drama</a>
        </div>

        <div class="endpoint">
            <h3><span class="method">GET</span> Movies by Runtime</h3>
            <div class="url">/api/movies/runtime/90/120?limit=10</div>
            <p>Get movies within a specific runtime range (in minutes).</p>
            <a href="/api/movies/runtime/90/120?limit=10" class="btn">90-120 min</a>
            <a href="/api/movies/runtime/120/180?limit=10" class="btn">2-3 hours</a>
        </div>

        <div class="endpoint">
            <h3><span class="method">GET</span> Longest Movies</h3>
            <div class="url">/api/movies/longest?limit=10</div>
            <p>Get the longest movies by runtime.</p>
            <a href="/api/movies/longest?limit=10" class="btn">Try it</a>
        </div>

        <div class="endpoint">
            <h3><span class="method">GET</span> Recent Movies</h3>
            <div class="url">/api/movies/recent?limit=10</div>
            <p>Get the most recently released movies.</p>
            <a href="/api/movies/recent?limit=10" class="btn">Try it</a>
        </div>

        <div class="endpoint">
            <h3><span class="method">GET</span> Movies Statistics by Year</h3>
            <div class="url">/api/stats/years</div>
            <p>Get movie count statistics by year (last 30 years).</p>
            <a href="/api/stats/years" class="btn">Try it</a>
        </div>

        <div class="endpoint">
            <h3><span class="method">GET</span> Genre Statistics</h3>
            <div class="url">/api/stats/genres</div>
            <p>Get statistics showing movie counts by genre combinations.</p>
            <a href="/api/stats/genres" class="btn">Try it</a>
        </div>

        <div class="endpoint">
            <h3><span class="method">GET</span> Runtime Statistics</h3>
            <div class="url">/api/stats/runtime</div>
            <p>Get runtime statistics (average, min, max).</p>
            <a href="/api/stats/runtime" class="btn">Try it</a>
        </div>

        <div class="endpoint">
            <h3><span class="method">GET</span> Advanced Search</h3>
            <div class="url">/api/search/advanced?q=action&type=genre_pattern</div>
            <p>Advanced search with pattern matching. Types: basic, regex, year_pattern, genre_pattern</p>
            <a href="/api/search/advanced?q=Action+Comedy&type=genre_pattern&limit=5" class="btn">Action+Comedy</a>
            <a href="/api/search/advanced?q=199*&type=year_pattern&limit=5" class="btn">1990s Movies</a>
        </div>

        <div class="endpoint">
            <h3><span class="method">GET</span> Regex Search</h3>
            <div class="url">/api/regex/search?pattern=^The.*man$</div>
            <p>Search movie titles using regular expressions.</p>
            <a href="/api/regex/search?pattern=^The.*&limit=5" class="btn">Starts with "The"</a>
            <a href="/api/regex/search?pattern=.*[0-9]+.*&limit=5" class="btn">Contains Numbers</a>
        </div>

        <div class="endpoint">
            <h3><span class="method">GET</span> Database Views</h3>
            <div class="url">/api/views/recent_quality_movies</div>
            <p>Access organized data through database views.</p>
            <a href="/api/views/recent_quality_movies?limit=10" class="btn">Recent Quality</a>
            <a href="/api/views/genre_stats_view?limit=10" class="btn">Genre Stats</a>
            <a href="/api/views/decade_summary?limit=10" class="btn">By Decade</a>
        </div>
    </div>

    <script>
        // Global variables for infinite scroll
        let currentSearchType = 'recent';
        let currentSearchTerm = '';
        let currentOffset = 0;
        let isLoading = false;
        let hasMoreMovies = true;

        // Movie lists management using database API
        async function fetchWantToWatchMovies() {
            try {
                const response = await fetch('/api/user/want-to-watch');
                const data = await response.json();
                return data.movies || [];
            } catch (error) {
                console.error('Error fetching want to watch movies:', error);
                return [];
            }
        }

        async function fetchWatchedMovies() {
            try {
                const response = await fetch('/api/user/watched');
                const data = await response.json();
                return data.movies || [];
            } catch (error) {
                console.error('Error fetching watched movies:', error);
                return [];
            }
        }

        async function addToWantToWatch(tconst) {
            try {
                const response = await fetch('/api/user/want-to-watch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tconst: tconst })
                });
                return response.ok;
            } catch (error) {
                console.error('Error adding to want to watch:', error);
                return false;
            }
        }

        async function removeFromWantToWatch(tconst) {
            try {
                const response = await fetch('/api/user/want-to-watch', {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tconst: tconst })
                });
                return response.ok;
            } catch (error) {
                console.error('Error removing from want to watch:', error);
                return false;
            }
        }

        async function addToWatched(tconst) {
            try {
                const response = await fetch('/api/user/watched', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tconst: tconst })
                });
                return response.ok;
            } catch (error) {
                console.error('Error adding to watched:', error);
                return false;
            }
        }

        async function removeFromWatched(tconst) {
            try {
                const response = await fetch('/api/user/watched', {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tconst: tconst })
                });
                return response.ok;
            } catch (error) {
                console.error('Error removing from watched:', error);
                return false;
            }
        }

        async function clearAllWantToWatch() {
            if (confirm('Are you sure you want to clear your entire want to watch list?')) {
                try {
                    const response = await fetch('/api/user/want-to-watch/clear', {
                        method: 'DELETE'
                    });
                    if (response.ok) {
                        await updateWantToWatchCount();
                        await displayWantToWatchMovies();
                    }
                } catch (error) {
                    console.error('Error clearing want to watch list:', error);
                }
            }
        }

        async function clearAllWatched() {
            if (confirm('Are you sure you want to clear all watched movies?')) {
                try {
                    const response = await fetch('/api/user/watched/clear', {
                        method: 'DELETE'
                    });
                    if (response.ok) {
                        await updateWatchedCount();
                        await displayWatchedMovies();
                    }
                } catch (error) {
                    console.error('Error clearing watched list:', error);
                }
            }
        }

        async function toggleWantToWatch(movie) {
            const wantToWatchMovies = await fetchWantToWatchMovies();
            const isCurrentlyWantToWatch = wantToWatchMovies.some(m => m.tconst === movie.tconst);
            
            let success = false;
            if (isCurrentlyWantToWatch) {
                success = await removeFromWantToWatch(movie.tconst);
            } else {
                success = await addToWantToWatch(movie.tconst);
            }
            
            if (success) {
                await updateWantToWatchCount();
                await displayWantToWatchMovies();
                // Refresh current view if it shows search results
                if (document.getElementById('searchResults').children.length > 0) {
                    await refreshCurrentView();
                }
            }
        }

        async function toggleWatched(movie) {
            const watchedMovies = await fetchWatchedMovies();
            const isCurrentlyWatched = watchedMovies.some(m => m.tconst === movie.tconst);
            
            let success = false;
            if (isCurrentlyWatched) {
                success = await removeFromWatched(movie.tconst);
            } else {
                success = await addToWatched(movie.tconst);
            }
            
            if (success) {
                await updateWatchedCount();
                await displayWatchedMovies();
                // Refresh current view if it shows search results
                if (document.getElementById('searchResults').children.length > 0) {
                    await refreshCurrentView();
                }
            }
        }

        async function updateWantToWatchCount() {
            try {
                const response = await fetch('/api/user/lists/summary');
                const data = await response.json();
                document.getElementById('wantToWatchCount').textContent = data.want_to_watch_count || 0;
            } catch (error) {
                console.error('Error updating want to watch count:', error);
            }
        }

        async function updateWatchedCount() {
            try {
                const response = await fetch('/api/user/lists/summary');
                const data = await response.json();
                document.getElementById('watchedCount').textContent = data.watched_count || 0;
            } catch (error) {
                console.error('Error updating watched count:', error);
            }
        }

        async function displayWantToWatchMovies() {
            const movies = await fetchWantToWatchMovies();
            const container = document.getElementById('wantToWatchMovies');
            
            if (movies.length === 0) {
                container.innerHTML = '<div class="no-results">No movies in your want to watch list yet. Add some movies!</div>';
                return;
            }

            container.innerHTML = movies.map(movie => `
                <div class="movie-item want-to-watch-movie">
                    <div class="movie-title">${movie.primaryTitle}</div>
                    <div class="movie-details">
                        ${movie.startYear || 'Unknown Year'} • 
                        ${movie.runtimeMinutes ? movie.runtimeMinutes + ' min' : 'Unknown runtime'}
                    </div>
                    ${movie.genres ? `<span class="movie-genres">${movie.genres}</span>` : ''}
                    <br><br>
                    <button onclick="toggleWantToWatch(${JSON.stringify(movie).replace(/"/g, '&quot;')})" class="btn btn-danger">
                        Remove from List
                    </button>
                </div>
            `).join('');
        }

        async function displayWatchedMovies() {
            const movies = await fetchWatchedMovies();
            const container = document.getElementById('watchedMovies');
            
            if (movies.length === 0) {
                container.innerHTML = '<div class="no-results">No watched movies yet. Mark some movies as watched!</div>';
                return;
            }

            container.innerHTML = movies.map(movie => `
                <div class="movie-item watched-movie">
                    <div class="movie-title">${movie.primaryTitle}</div>
                    <div class="movie-details">
                        ${movie.startYear || 'Unknown Year'} • 
                        ${movie.runtimeMinutes ? movie.runtimeMinutes + ' min' : 'Unknown runtime'}
                    </div>
                    ${movie.genres ? `<span class="movie-genres">${movie.genres}</span>` : ''}
                    <br><br>
                    <button onclick="toggleWatched(${JSON.stringify(movie).replace(/"/g, '&quot;')})" class="btn btn-secondary">
                        Mark as Unwatched
                    </button>
                </div>
            `).join('');
        }

        async function isMovieWantToWatch(movieId) {
            const movies = await fetchWantToWatchMovies();
            return movies.some(m => m.tconst === movieId);
        }

        async function isMovieWatched(movieId) {
            const movies = await fetchWatchedMovies();
            return movies.some(m => m.tconst === movieId);
        }

        async function displayMovies(movies, containerId, append = false) {
            const container = document.getElementById(containerId);
            
            if (movies.length === 0 && !append) {
                container.innerHTML = '<div class="no-results">No movies found.</div>';
                return;
            }

            // Get current movie lists for status checking
            const wantToWatchMovies = await fetchWantToWatchMovies();
            const watchedMovies = await fetchWatchedMovies();
            
            const moviesHtml = await Promise.all(movies.map(async movie => {
                const isWantToWatch = wantToWatchMovies.some(m => m.tconst === movie.tconst);
                const isWatched = watchedMovies.some(m => m.tconst === movie.tconst);
                let movieClasses = 'movie-item';
                if (isWantToWatch) movieClasses += ' want-to-watch-movie';
                if (isWatched) movieClasses += ' watched-movie';
                
                return `
                    <div class="${movieClasses}">
                        <div class="movie-title">
                            ${movie.primaryTitle}
                            ${isWatched ? '<span style="color: #6c757d; font-size: 14px; margin-left: 10px;">👁️ Watched</span>' : ''}
                        </div>
                        <div class="movie-details">
                            ${movie.startYear || 'Unknown Year'} • 
                            ${movie.runtimeMinutes ? movie.runtimeMinutes + ' min' : 'Unknown runtime'}
                        </div>
                        ${movie.genres ? `<span class="movie-genres">${movie.genres}</span>` : ''}
                        <br><br>
                        <button onclick="toggleWantToWatch(${JSON.stringify(movie).replace(/"/g, '&quot;')})" 
                                class="btn ${isWantToWatch ? 'btn-danger' : 'btn-success'}">
                            ${isWantToWatch ? '💔 Remove from List' : '❤️ Add to List'}
                        </button>
                        <button onclick="toggleWatched(${JSON.stringify(movie).replace(/"/g, '&quot;')})" 
                                class="btn ${isWatched ? 'btn-secondary' : 'btn-info'}">
                            ${isWatched ? '👁️ Watched' : '📺 Mark as Watched'}
                        </button>
                    </div>
                `;
            }));
            
            if (append) {
                container.innerHTML += moviesHtml.join('');
            } else {
                container.innerHTML = moviesHtml.join('');
            }
            
            // Add load more button if there are more movies
            if (hasMoreMovies && containerId === 'searchResults') {
                const loadMoreBtn = `
                    <div class="load-more-container">
                        <button onclick="loadMoreMovies()" class="btn" id="loadMoreBtn">
                            Load More Movies
                        </button>
                    </div>
                `;
                container.innerHTML += loadMoreBtn;
            }
        }

        // Helper function to refresh current view after movie list changes
        async function refreshCurrentView() {
            // This would ideally re-run the current search/view
            // For now, we'll just update the visual states
            const searchResults = document.getElementById('searchResults');
            if (searchResults && searchResults.children.length > 0) {
                // Re-render the current search results with updated states
                // This is a simplified approach - in a more complex app you'd store the current search state
            }
        }

        // Search movies
        function searchMovies() {
            const query = document.getElementById('searchInput').value.trim();
            if (!query) {
                alert('Please enter a search term');
                return;
            }

            // Reset for new search
            currentSearchType = 'search';
            currentSearchTerm = query;
            currentOffset = 0;
            hasMoreMovies = true;

            const container = document.getElementById('searchResults');
            container.innerHTML = '<div class="loading">Searching...</div>';

            fetch(`/api/movies/search?q=${encodeURIComponent(query)}&limit=20&offset=0`)
                .then(response => response.json())
                .then(data => {
                    hasMoreMovies = data.has_more || false;
                    currentOffset = 20;
                    displayMovies(data.movies, 'searchResults');
                })
                .catch(error => {
                    container.innerHTML = '<div class="no-results">Error searching movies</div>';
                });
        }

        // Search by genre
        function searchByGenre() {
            const genre = prompt('Enter a genre (e.g., Action, Comedy, Drama):');
            if (!genre) return;

            // Reset for new search
            currentSearchType = 'genre';
            currentSearchTerm = genre;
            currentOffset = 0;
            hasMoreMovies = true;

            const container = document.getElementById('searchResults');
            container.innerHTML = '<div class="loading">Searching...</div>';

            fetch(`/api/movies/genre/${encodeURIComponent(genre)}?limit=20&offset=0`)
                .then(response => response.json())
                .then(data => {
                    hasMoreMovies = data.has_more || false;
                    currentOffset = 20;
                    displayMovies(data.movies, 'searchResults');
                })
                .catch(error => {
                    container.innerHTML = '<div class="no-results">Error searching movies</div>';
                });
        }

        // Get recent movies
        function getRecentMovies() {
            // Reset for new search
            currentSearchType = 'recent';
            currentSearchTerm = '';
            currentOffset = 0;
            hasMoreMovies = true;

            const container = document.getElementById('searchResults');
            container.innerHTML = '<div class="loading">Loading recent movies...</div>';

            fetch('/api/movies/recent?limit=20&offset=0')
                .then(response => response.json())
                .then(data => {
                    hasMoreMovies = data.has_more || false;
                    currentOffset = 20;
                    displayMovies(data.movies, 'searchResults');
                })
                .catch(error => {
                    container.innerHTML = '<div class="no-results">Error loading movies</div>';
                });
        }

        // Load more movies (infinite scroll)
        function loadMoreMovies() {
            if (isLoading || !hasMoreMovies) return;
            
            isLoading = true;
            const loadMoreBtn = document.getElementById('loadMoreBtn');
            if (loadMoreBtn) {
                loadMoreBtn.textContent = 'Loading...';
                loadMoreBtn.disabled = true;
            }

            let url = '';
            switch (currentSearchType) {
                case 'search':
                    url = `/api/movies/search?q=${encodeURIComponent(currentSearchTerm)}&limit=20&offset=${currentOffset}`;
                    break;
                case 'genre':
                    url = `/api/movies/genre/${encodeURIComponent(currentSearchTerm)}?limit=20&offset=${currentOffset}`;
                    break;
                case 'recent':
                    url = `/api/movies/recent?limit=20&offset=${currentOffset}`;
                    break;
                case 'regex':
                    url = `/api/regex/search?pattern=${encodeURIComponent(currentSearchTerm)}&limit=20&offset=${currentOffset}`;
                    break;
                default:
                    url = `/api/movies/recent?limit=20&offset=${currentOffset}`;
            }

            fetch(url)
                .then(response => response.json())
                .then(data => {
                    hasMoreMovies = data.has_more || false;
                    currentOffset += 20;
                    
                    // Remove existing load more button
                    if (loadMoreBtn && loadMoreBtn.parentElement) {
                        loadMoreBtn.parentElement.remove();
                    }
                    
                    // Append new movies
                    displayMovies(data.movies, 'searchResults', true);
                })
                .catch(error => {
                    console.error('Error loading more movies:', error);
                })
                .finally(() => {
                    isLoading = false;
                });
        }

        // Regex search
        function regexSearch() {
            const pattern = prompt('Enter a regex pattern (e.g., "^The.*man$" for titles starting with "The" and ending with "man"):');
            if (!pattern) return;

            // Reset for new search
            currentSearchType = 'regex';
            currentSearchTerm = pattern;
            currentOffset = 0;
            hasMoreMovies = true;

            const container = document.getElementById('searchResults');
            container.innerHTML = '<div class="loading">Searching with regex pattern...</div>';

            fetch(`/api/regex/search?pattern=${encodeURIComponent(pattern)}&limit=20`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        container.innerHTML = `<div class="no-results">Error: ${data.error}</div>`;
                    } else {
                        hasMoreMovies = data.has_more || false;
                        currentOffset = 20;
                        displayMovies(data.movies, 'searchResults');
                    }
                })
                .catch(error => {
                    container.innerHTML = '<div class="no-results">Error with regex search</div>';
                });
        }

        // Get recommendations
        async function getRecommendations() {
            const wantToWatchMovies = await fetchWantToWatchMovies();
            const watchedMovies = await fetchWatchedMovies();
            const totalInteractions = wantToWatchMovies.length + watchedMovies.length;
            
            if (totalInteractions < 5) {
                alert(`Please interact with at least 5 movies to get recommendations! You currently have ${totalInteractions} interactions (${wantToWatchMovies.length} want to watch + ${watchedMovies.length} watched).`);
                return;
            }

            const container = document.getElementById('recommendations');
            container.innerHTML = '<div class="loading">Generating recommendations based on your movie preferences...</div>';

            try {
                const response = await fetch('/api/recommendations', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                
                const data = await response.json();
                
                if (data.recommendations && data.recommendations.length > 0) {
                    container.innerHTML = `
                        <h3>🎬 Recommended for You (${data.recommendations.length} movies)</h3>
                        <p>Based on your preferences from ${data.analysis.total_interactions} movie interactions</p>
                        <p><strong>Top genres:</strong> ${data.analysis.top_genres.join(', ')}</p>
                    `;
                    await displayMovies(data.recommendations, 'recommendations');
                } else {
                    let errorMsg = 'No recommendations found. Try adding more movies to your lists!';
                    if (data.analysis && data.analysis.error) {
                        errorMsg = `Error: ${data.analysis.error}`;
                    }
                    if (data.analysis && data.analysis.top_genres && data.analysis.top_genres.length > 0) {
                        errorMsg += `<br><br>Debug info: Found genres: ${data.analysis.top_genres.join(', ')}`;
                    }
                    container.innerHTML = `<div class="no-results">${errorMsg}</div>`;
                }
            } catch (error) {
                container.innerHTML = '<div class="no-results">Error generating recommendations</div>';
                console.error('Error getting recommendations:', error);
            }
        }

        // Allow Enter key to trigger search
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchMovies();
            }
        });

        // Initialize the page
        document.addEventListener('DOMContentLoaded', async function() {
            await updateWantToWatchCount();
            await displayWantToWatchMovies();
            await updateWatchedCount();
            await displayWatchedMovies();
            getRecentMovies(); // Load some initial movies with pagination support
        });

        // Load statistics on page load
        fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                const statsDiv = document.getElementById('stats');
                statsDiv.innerHTML = `
                    <div class="stat-card">
                        <div class="stat-number">${data.total_movies.toLocaleString()}</div>
                        <div>Total Movies</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.movies_with_year.toLocaleString()}</div>
                        <div>Movies with Year</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.year_range || 'N/A'}</div>
                        <div>Year Range</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.unique_genre_combinations}</div>
                        <div>Genre Combinations</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.non_adult_movies.toLocaleString()}</div>
                        <div>Family-Friendly</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.adult_movies.toLocaleString()}</div>
                        <div>Adult Movies</div>
                    </div>
                `;
            })
            .catch(error => {
                document.getElementById('stats').innerHTML = '<p>Error loading statistics</p>';
            });
    </script>
</body>
</html>
"""

# HTML template for the dashboard
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IMDb Movies Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
        }
        .dashboard-container {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        .panel {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .search-container {
            margin-bottom: 20px;
        }
        .search-box {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            margin-bottom: 10px;
        }
        .search-box:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            background: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            margin: 5px;
        }
        .btn:hover {
            background: #0056b3;
        }
        .btn-success {
            background: #28a745;
        }
        .btn-success:hover {
            background: #1e7e34;
        }
        .btn-danger {
            background: #dc3545;
        }
        .btn-danger:hover {
            background: #bd2130;
        }
        .btn-large {
            padding: 15px 30px;
            font-size: 16px;
            font-weight: bold;
        }
        .btn-info {
            background: #17a2b8;
        }
        .btn-info:hover {
            background: #138496;
        }
        .btn-secondary {
            background: #6c757d;
        }
        .btn-secondary:hover {
            background: #545b62;
        }
        .movie-item {
            border: 1px solid #eee;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            background: #fafafa;
            transition: all 0.3s ease;
        }
        .movie-item:hover {
            background: #f0f0f0;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .movie-title {
            font-weight: bold;
            font-size: 18px;
            color: #333;
            margin-bottom: 5px;
        }
        .movie-details {
            color: #666;
            font-size: 14px;
            margin-bottom: 10px;
        }
        .movie-genres {
            background: #e9ecef;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            display: inline-block;
            margin-right: 5px;
        }
        .want-to-watch-movie {
            border-color: #28a745;
            background: #f8fff9;
        }
        .watched-movie {
            border-color: #17a2b8;
            background: #f0f9ff;
        }
        .movie-item.want-to-watch-movie.watched-movie {
            border-color: #6f42c1;
            background: #f8f9ff;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        .no-results {
            text-align: center;
            padding: 20px;
            color: #999;
            font-style: italic;
        }
        .recommendation-section {
            grid-column: 1 / -1;
            margin-top: 20px;
        }
        .stats-bar {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }
        .stats-number {
            font-size: 24px;
            font-weight: bold;
            color: #1976d2;
        }
        .clear-btn {
            background: #6c757d;
            float: right;
        }
        .clear-btn:hover {
            background: #545b62;
        }
        .load-more-container {
            text-align: center;
            margin: 20px 0;
            padding: 15px;
        }
        .load-more-container .btn {
            background: #28a745;
            font-size: 16px;
            padding: 12px 30px;
        }
        .load-more-container .btn:hover {
            background: #1e7e34;
        }
        .load-more-container .btn:disabled {
            background: #6c757d;
            cursor: not-allowed;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎬 IMDb Movies Dashboard</h1>
        <p>Search, Like, and Get Personalized Movie Recommendations</p>
        <a href="/" class="btn" style="margin-top: 15px;">Back to API Docs</a>
    </div>

    <div class="dashboard-container">
        <!-- Search Panel -->
        <div class="panel">
            <h2>🔍 Search Movies</h2>
            <div class="search-container">
                <input type="text" id="searchInput" class="search-box" placeholder="Search for movies..." />
                <button onclick="searchMovies()" class="btn">Search</button>
                <button onclick="searchByGenre()" class="btn">Search by Genre</button>
                <button onclick="getRecentMovies()" class="btn">Recent Movies</button>
                <button onclick="regexSearch()" class="btn">Regex Search</button>
            </div>
            <div id="searchResults"></div>
        </div>

        <!-- Want to Watch Panel -->
        <div class="panel">
            <h2>❤️ Your Want to Watch</h2>
            <div class="stats-bar">
                <div class="stats-number" id="wantToWatchCount">0</div>
                <div>Movies Want to Watch</div>
            </div>
            <button onclick="clearAllWantToWatch()" class="btn clear-btn">Clear All</button>
            <div id="wantToWatchMovies"></div>
        </div>

        <!-- Already Watched Panel -->
        <div class="panel">
            <h2>👁️ Already Watched</h2>
            <div class="stats-bar">
                <div class="stats-number" id="watchedCount">0</div>
                <div>Movies Watched</div>
            </div>
            <button onclick="clearAllWatched()" class="btn clear-btn">Clear All</button>
            <div id="watchedMovies"></div>
        </div>
    </div>

    <!-- Recommendations Panel -->
    <div class="panel recommendation-section">
        <h2>🎯 Personalized Recommendations</h2>
        <p>Add at least 5 movies to your lists (want to watch + already watched) and we'll find similar films you might enjoy!</p>
        <button onclick="getRecommendations()" class="btn btn-large">Generate Recommendations</button>
        <div id="recommendations"></div>
    </div>

    <script>
        // Global variables for infinite scroll
        let currentSearchType = 'recent';
        let currentSearchTerm = '';
        let currentOffset = 0;
        let isLoading = false;
        let hasMoreMovies = true;

        // Movie lists management using database API
        async function fetchWantToWatchMovies() {
            try {
                const response = await fetch('/api/user/want-to-watch');
                const data = await response.json();
                return data.movies || [];
            } catch (error) {
                console.error('Error fetching want to watch movies:', error);
                return [];
            }
        }

        async function fetchWatchedMovies() {
            try {
                const response = await fetch('/api/user/watched');
                const data = await response.json();
                return data.movies || [];
            } catch (error) {
                console.error('Error fetching watched movies:', error);
                return [];
            }
        }

        async function addToWantToWatch(tconst) {
            try {
                const response = await fetch('/api/user/want-to-watch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tconst: tconst })
                });
                return response.ok;
            } catch (error) {
                console.error('Error adding to want to watch:', error);
                return false;
            }
        }

        async function removeFromWantToWatch(tconst) {
            try {
                const response = await fetch('/api/user/want-to-watch', {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tconst: tconst })
                });
                return response.ok;
            } catch (error) {
                console.error('Error removing from want to watch:', error);
                return false;
            }
        }

        async function addToWatched(tconst) {
            try {
                const response = await fetch('/api/user/watched', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tconst: tconst })
                });
                return response.ok;
            } catch (error) {
                console.error('Error adding to watched:', error);
                return false;
            }
        }

        async function removeFromWatched(tconst) {
            try {
                const response = await fetch('/api/user/watched', {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tconst: tconst })
                });
                return response.ok;
            } catch (error) {
                console.error('Error removing from watched:', error);
                return false;
            }
        }

        async function clearAllWantToWatch() {
            if (confirm('Are you sure you want to clear your entire want to watch list?')) {
                try {
                    const response = await fetch('/api/user/want-to-watch/clear', {
                        method: 'DELETE'
                    });
                    if (response.ok) {
                        await updateWantToWatchCount();
                        await displayWantToWatchMovies();
                    }
                } catch (error) {
                    console.error('Error clearing want to watch list:', error);
                }
            }
        }

        async function clearAllWatched() {
            if (confirm('Are you sure you want to clear all watched movies?')) {
                try {
                    const response = await fetch('/api/user/watched/clear', {
                        method: 'DELETE'
                    });
                    if (response.ok) {
                        await updateWatchedCount();
                        await displayWatchedMovies();
                    }
                } catch (error) {
                    console.error('Error clearing watched list:', error);
                }
            }
        }

        async function toggleWantToWatch(movie) {
            const wantToWatchMovies = await fetchWantToWatchMovies();
            const isCurrentlyWantToWatch = wantToWatchMovies.some(m => m.tconst === movie.tconst);
            
            let success = false;
            if (isCurrentlyWantToWatch) {
                success = await removeFromWantToWatch(movie.tconst);
            } else {
                success = await addToWantToWatch(movie.tconst);
            }
            
            if (success) {
                await updateWantToWatchCount();
                await displayWantToWatchMovies();
                // Refresh current view if it shows search results
                if (document.getElementById('searchResults').children.length > 0) {
                    await refreshCurrentView();
                }
            }
        }

        async function toggleWatched(movie) {
            const watchedMovies = await fetchWatchedMovies();
            const isCurrentlyWatched = watchedMovies.some(m => m.tconst === movie.tconst);
            
            let success = false;
            if (isCurrentlyWatched) {
                success = await removeFromWatched(movie.tconst);
            } else {
                success = await addToWatched(movie.tconst);
            }
            
            if (success) {
                await updateWatchedCount();
                await displayWatchedMovies();
                // Refresh current view if it shows search results
                if (document.getElementById('searchResults').children.length > 0) {
                    await refreshCurrentView();
                }
            }
        }

        async function updateWantToWatchCount() {
            try {
                const response = await fetch('/api/user/lists/summary');
                const data = await response.json();
                document.getElementById('wantToWatchCount').textContent = data.want_to_watch_count || 0;
            } catch (error) {
                console.error('Error updating want to watch count:', error);
            }
        }

        async function updateWatchedCount() {
            try {
                const response = await fetch('/api/user/lists/summary');
                const data = await response.json();
                document.getElementById('watchedCount').textContent = data.watched_count || 0;
            } catch (error) {
                console.error('Error updating watched count:', error);
            }
        }

        async function displayWantToWatchMovies() {
            const movies = await fetchWantToWatchMovies();
            const container = document.getElementById('wantToWatchMovies');
            
            if (movies.length === 0) {
                container.innerHTML = '<div class="no-results">No movies in your want to watch list yet. Add some movies!</div>';
                return;
            }

            container.innerHTML = movies.map(movie => `
                <div class="movie-item want-to-watch-movie">
                    <div class="movie-title">${movie.primaryTitle}</div>
                    <div class="movie-details">
                        ${movie.startYear || 'Unknown Year'} • 
                        ${movie.runtimeMinutes ? movie.runtimeMinutes + ' min' : 'Unknown runtime'}
                    </div>
                    ${movie.genres ? `<span class="movie-genres">${movie.genres}</span>` : ''}
                    <br><br>
                    <button onclick="toggleWantToWatch(${JSON.stringify(movie).replace(/"/g, '&quot;')})" class="btn btn-danger">
                        Remove from List
                    </button>
                </div>
            `).join('');
        }

        async function displayWatchedMovies() {
            const movies = await fetchWatchedMovies();
            const container = document.getElementById('watchedMovies');
            
            if (movies.length === 0) {
                container.innerHTML = '<div class="no-results">No watched movies yet. Mark some movies as watched!</div>';
                return;
            }

            container.innerHTML = movies.map(movie => `
                <div class="movie-item watched-movie">
                    <div class="movie-title">${movie.primaryTitle}</div>
                    <div class="movie-details">
                        ${movie.startYear || 'Unknown Year'} • 
                        ${movie.runtimeMinutes ? movie.runtimeMinutes + ' min' : 'Unknown runtime'}
                    </div>
                    ${movie.genres ? `<span class="movie-genres">${movie.genres}</span>` : ''}
                    <br><br>
                    <button onclick="toggleWatched(${JSON.stringify(movie).replace(/"/g, '&quot;')})" class="btn btn-secondary">
                        Mark as Unwatched
                    </button>
                </div>
            `).join('');
        }

        async function isMovieWantToWatch(movieId) {
            const movies = await fetchWantToWatchMovies();
            return movies.some(m => m.tconst === movieId);
        }

        async function isMovieWatched(movieId) {
            const movies = await fetchWatchedMovies();
            return movies.some(m => m.tconst === movieId);
        }

        async function displayMovies(movies, containerId, append = false) {
            const container = document.getElementById(containerId);
            
            if (movies.length === 0 && !append) {
                container.innerHTML = '<div class="no-results">No movies found.</div>';
                return;
            }

            // Get current movie lists for status checking
            const wantToWatchMovies = await fetchWantToWatchMovies();
            const watchedMovies = await fetchWatchedMovies();
            
            const moviesHtml = await Promise.all(movies.map(async movie => {
                const isWantToWatch = wantToWatchMovies.some(m => m.tconst === movie.tconst);
                const isWatched = watchedMovies.some(m => m.tconst === movie.tconst);
                let movieClasses = 'movie-item';
                if (isWantToWatch) movieClasses += ' want-to-watch-movie';
                if (isWatched) movieClasses += ' watched-movie';
                
                return `
                    <div class="${movieClasses}">
                        <div class="movie-title">
                            ${movie.primaryTitle}
                            ${isWatched ? '<span style="color: #6c757d; font-size: 14px; margin-left: 10px;">👁️ Watched</span>' : ''}
                        </div>
                        <div class="movie-details">
                            ${movie.startYear || 'Unknown Year'} • 
                            ${movie.runtimeMinutes ? movie.runtimeMinutes + ' min' : 'Unknown runtime'}
                        </div>
                        ${movie.genres ? `<span class="movie-genres">${movie.genres}</span>` : ''}
                        <br><br>
                        <button onclick="toggleWantToWatch(${JSON.stringify(movie).replace(/"/g, '&quot;')})" 
                                class="btn ${isWantToWatch ? 'btn-danger' : 'btn-success'}">
                            ${isWantToWatch ? '💔 Remove from List' : '❤️ Add to List'}
                        </button>
                        <button onclick="toggleWatched(${JSON.stringify(movie).replace(/"/g, '&quot;')})" 
                                class="btn ${isWatched ? 'btn-secondary' : 'btn-info'}">
                            ${isWatched ? '👁️ Watched' : '📺 Mark as Watched'}
                        </button>
                    </div>
                `;
            }));
            
            if (append) {
                container.innerHTML += moviesHtml.join('');
            } else {
                container.innerHTML = moviesHtml.join('');
            }
            
            // Add load more button if there are more movies
            if (hasMoreMovies && containerId === 'searchResults') {
                const loadMoreBtn = `
                    <div class="load-more-container">
                        <button onclick="loadMoreMovies()" class="btn" id="loadMoreBtn">
                            Load More Movies
                        </button>
                    </div>
                `;
                container.innerHTML += loadMoreBtn;
            }
        }

        // Helper function to refresh current view after movie list changes
        async function refreshCurrentView() {
            // This would ideally re-run the current search/view
            // For now, we'll just update the visual states
            const searchResults = document.getElementById('searchResults');
            if (searchResults && searchResults.children.length > 0) {
                // Re-render the current search results with updated states
                // This is a simplified approach - in a more complex app you'd store the current search state
            }
        }

        // Search movies
        function searchMovies() {
            const query = document.getElementById('searchInput').value.trim();
            if (!query) {
                alert('Please enter a search term');
                return;
            }

            // Reset for new search
            currentSearchType = 'search';
            currentSearchTerm = query;
            currentOffset = 0;
            hasMoreMovies = true;

            const container = document.getElementById('searchResults');
            container.innerHTML = '<div class="loading">Searching...</div>';

            fetch(`/api/movies/search?q=${encodeURIComponent(query)}&limit=20&offset=0`)
                .then(response => response.json())
                .then(data => {
                    hasMoreMovies = data.has_more || false;
                    currentOffset = 20;
                    displayMovies(data.movies, 'searchResults');
                })
                .catch(error => {
                    container.innerHTML = '<div class="no-results">Error searching movies</div>';
                });
        }

        // Search by genre
        function searchByGenre() {
            const genre = prompt('Enter a genre (e.g., Action, Comedy, Drama):');
            if (!genre) return;

            // Reset for new search
            currentSearchType = 'genre';
            currentSearchTerm = genre;
            currentOffset = 0;
            hasMoreMovies = true;

            const container = document.getElementById('searchResults');
            container.innerHTML = '<div class="loading">Searching...</div>';

            fetch(`/api/movies/genre/${encodeURIComponent(genre)}?limit=20&offset=0`)
                .then(response => response.json())
                .then(data => {
                    hasMoreMovies = data.has_more || false;
                    currentOffset = 20;
                    displayMovies(data.movies, 'searchResults');
                })
                .catch(error => {
                    container.innerHTML = '<div class="no-results">Error searching movies</div>';
                });
        }

        // Get recent movies
        function getRecentMovies() {
            // Reset for new search
            currentSearchType = 'recent';
            currentSearchTerm = '';
            currentOffset = 0;
            hasMoreMovies = true;

            const container = document.getElementById('searchResults');
            container.innerHTML = '<div class="loading">Loading recent movies...</div>';

            fetch('/api/movies/recent?limit=20&offset=0')
                .then(response => response.json())
                .then(data => {
                    hasMoreMovies = data.has_more || false;
                    currentOffset = 20;
                    displayMovies(data.movies, 'searchResults');
                })
                .catch(error => {
                    container.innerHTML = '<div class="no-results">Error loading movies</div>';
                });
        }

        // Load more movies (infinite scroll)
        function loadMoreMovies() {
            if (isLoading || !hasMoreMovies) return;
            
            isLoading = true;
            const loadMoreBtn = document.getElementById('loadMoreBtn');
            if (loadMoreBtn) {
                loadMoreBtn.textContent = 'Loading...';
                loadMoreBtn.disabled = true;
            }

            let url = '';
            switch (currentSearchType) {
                case 'search':
                    url = `/api/movies/search?q=${encodeURIComponent(currentSearchTerm)}&limit=20&offset=${currentOffset}`;
                    break;
                case 'genre':
                    url = `/api/movies/genre/${encodeURIComponent(currentSearchTerm)}?limit=20&offset=${currentOffset}`;
                    break;
                case 'recent':
                    url = `/api/movies/recent?limit=20&offset=${currentOffset}`;
                    break;
                case 'regex':
                    url = `/api/regex/search?pattern=${encodeURIComponent(currentSearchTerm)}&limit=20&offset=${currentOffset}`;
                    break;
                default:
                    url = `/api/movies/recent?limit=20&offset=${currentOffset}`;
            }

            fetch(url)
                .then(response => response.json())
                .then(data => {
                    hasMoreMovies = data.has_more || false;
                    currentOffset += 20;
                    
                    // Remove existing load more button
                    if (loadMoreBtn && loadMoreBtn.parentElement) {
                        loadMoreBtn.parentElement.remove();
                    }
                    
                    // Append new movies
                    displayMovies(data.movies, 'searchResults', true);
                })
                .catch(error => {
                    console.error('Error loading more movies:', error);
                })
                .finally(() => {
                    isLoading = false;
                });
        }

        // Regex search
        function regexSearch() {
            const pattern = prompt('Enter a regex pattern (e.g., "^The.*man$" for titles starting with "The" and ending with "man"):');
            if (!pattern) return;

            // Reset for new search
            currentSearchType = 'regex';
            currentSearchTerm = pattern;
            currentOffset = 0;
            hasMoreMovies = true;

            const container = document.getElementById('searchResults');
            container.innerHTML = '<div class="loading">Searching with regex pattern...</div>';

            fetch(`/api/regex/search?pattern=${encodeURIComponent(pattern)}&limit=20`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        container.innerHTML = `<div class="no-results">Error: ${data.error}</div>`;
                    } else {
                        hasMoreMovies = data.has_more || false;
                        currentOffset = 20;
                        displayMovies(data.movies, 'searchResults');
                    }
                })
                .catch(error => {
                    container.innerHTML = '<div class="no-results">Error with regex search</div>';
                });
        }

        // Get recommendations
        async function getRecommendations() {
            const wantToWatchMovies = await fetchWantToWatchMovies();
            const watchedMovies = await fetchWatchedMovies();
            const totalInteractions = wantToWatchMovies.length + watchedMovies.length;
            
            if (totalInteractions < 5) {
                alert(`Please interact with at least 5 movies to get recommendations! You currently have ${totalInteractions} interactions (${wantToWatchMovies.length} want to watch + ${watchedMovies.length} watched).`);
                return;
            }

            const container = document.getElementById('recommendations');
            container.innerHTML = '<div class="loading">Generating recommendations based on your movie preferences...</div>';

            try {
                const response = await fetch('/api/recommendations', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                
                const data = await response.json();
                
                if (data.recommendations && data.recommendations.length > 0) {
                    container.innerHTML = `
                        <h3>🎬 Recommended for You (${data.recommendations.length} movies)</h3>
                        <p>Based on your preferences from ${data.analysis.total_interactions} movie interactions</p>
                        <p><strong>Top genres:</strong> ${data.analysis.top_genres.join(', ')}</p>
                    `;
                    await displayMovies(data.recommendations, 'recommendations');
                } else {
                    let errorMsg = 'No recommendations found. Try adding more movies to your lists!';
                    if (data.analysis && data.analysis.error) {
                        errorMsg = `Error: ${data.analysis.error}`;
                    }
                    if (data.analysis && data.analysis.top_genres && data.analysis.top_genres.length > 0) {
                        errorMsg += `<br><br>Debug info: Found genres: ${data.analysis.top_genres.join(', ')}`;
                    }
                    container.innerHTML = `<div class="no-results">${errorMsg}</div>`;
                }
            } catch (error) {
                container.innerHTML = '<div class="no-results">Error generating recommendations</div>';
                console.error('Error getting recommendations:', error);
            }
        }

        // Allow Enter key to trigger search
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchMovies();
            }
        });

        // Initialize the page
        document.addEventListener('DOMContentLoaded', async function() {
            await updateWantToWatchCount();
            await displayWantToWatchMovies();
            await updateWatchedCount();
            await displayWatchedMovies();
            getRecentMovies(); // Load some initial movies with pagination support
        });

        // Load statistics on page load
        fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                const statsDiv = document.getElementById('stats');
                statsDiv.innerHTML = `
                    <div class="stat-card">
                        <div class="stat-number">${data.total_movies.toLocaleString()}</div>
                        <div>Total Movies</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.movies_with_year.toLocaleString()}</div>
                        <div>Movies with Year</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.year_range || 'N/A'}</div>
                        <div>Year Range</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.unique_genre_combinations}</div>
                        <div>Genre Combinations</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.non_adult_movies.toLocaleString()}</div>
                        <div>Family-Friendly</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.adult_movies.toLocaleString()}</div>
                        <div>Adult Movies</div>
                    </div>
                `;
            })
            .catch(error => {
                document.getElementById('stats').innerHTML = '<p>Error loading statistics</p>';
            });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main page with API documentation"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/stats')
def database_stats():
    """Get database statistics"""
    try:
        stats = queries.get_database_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/movies')
def get_movies():
    """Get sample movies"""
    limit = request.args.get('limit', 10, type=int)
    try:
        movies = queries.get_sample_movies(limit)
        return jsonify({
            'count': len(movies),
            'movies': movies
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/movies/year/<int:year>')
def get_movies_by_year(year):
    """Get movies by year"""
    limit = request.args.get('limit', 10, type=int)
    try:
        movies = queries.get_movies_by_year(year, limit)
        return jsonify({
            'year': year,
            'count': len(movies),
            'movies': movies
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/movies/years/<int:start_year>/<int:end_year>')
def get_movies_by_year_range(start_year, end_year):
    """Get movies by year range"""
    limit = request.args.get('limit', 10, type=int)
    try:
        movies = queries.get_movies_by_year_range(start_year, end_year, limit)
        return jsonify({
            'year_range': f"{start_year}-{end_year}",
            'count': len(movies),
            'movies': movies
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/movies/search')
def search_movies():
    """Search movies"""
    search_term = request.args.get('q', '')
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    if not search_term:
        return jsonify({'error': 'Search term (q) is required'}), 400
    
    try:
        movies = queries.search_movies(search_term, limit, offset)
        return jsonify({
            'search_term': search_term,
            'count': len(movies),
            'offset': offset,
            'has_more': len(movies) == limit,
            'movies': movies
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/movies/genre/<genre>')
def get_movies_by_genre(genre):
    """Get movies by genre"""
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    try:
        movies = queries.get_movies_by_genre(genre, limit, offset)
        return jsonify({
            'genre': genre,
            'count': len(movies),
            'offset': offset,
            'has_more': len(movies) == limit,
            'movies': movies
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/movies/runtime/<int:min_runtime>/<int:max_runtime>')
def get_movies_by_runtime(min_runtime, max_runtime):
    """Get movies by runtime range"""
    limit = request.args.get('limit', 10, type=int)
    try:
        movies = queries.get_movies_by_runtime(min_runtime, max_runtime, limit)
        return jsonify({
            'runtime_range': f"{min_runtime}-{max_runtime} minutes",
            'count': len(movies),
            'movies': movies
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/movies/longest')
def get_longest_movies():
    """Get longest movies"""
    limit = request.args.get('limit', 10, type=int)
    try:
        movies = queries.get_longest_movies(limit)
        return jsonify({
            'count': len(movies),
            'movies': movies
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/movies/recent')
def get_recent_movies():
    """Get recent movies"""
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    try:
        movies = queries.get_recent_movies(limit, offset)
        return jsonify({
            'count': len(movies),
            'offset': offset,
            'has_more': len(movies) == limit,
            'movies': movies
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats/years')
def get_movies_stats_by_year():
    """Get movie statistics by year"""
    try:
        stats = queries.get_movies_stats_by_year()
        return jsonify({
            'count': len(stats),
            'years': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats/genres')
def get_genre_stats():
    """Get genre statistics"""
    try:
        stats = queries.get_genre_stats()
        return jsonify({
            'count': len(stats),
            'genres': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats/runtime')
def get_runtime_stats():
    """Get runtime statistics"""
    try:
        stats = queries.get_runtime_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard')
def dashboard():
    """Movie dashboard with search and recommendations"""
    return render_template_string(DASHBOARD_TEMPLATE)

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Get movie recommendations based on want to watch and watched movies"""
    try:
        user_session = get_user_session()
        
        # Get user's movie lists from database
        want_to_watch_movies = queries.get_want_to_watch_movies(user_session)
        watched_movies = queries.get_watched_movies(user_session)
        
        want_to_watch_ids = [movie['tconst'] for movie in want_to_watch_movies]
        watched_ids = [movie['tconst'] for movie in watched_movies]
        
        total_interactions = len(want_to_watch_ids) + len(watched_ids)
        
        if total_interactions < 5:
            return jsonify({
                'error': f'At least 5 movie interactions required. Current: {total_interactions}'
            }), 400
        
        recommendations = queries.get_recommendations(want_to_watch_ids, watched_ids)
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search/advanced')
def advanced_search():
    """Advanced search with regex and pattern matching"""
    search_term = request.args.get('q', '')
    search_type = request.args.get('type', 'basic')  # basic, regex, year_pattern, genre_pattern
    limit = request.args.get('limit', 10, type=int)
    
    if not search_term:
        return jsonify({'error': 'Search term (q) is required'}), 400
    
    try:
        movies = queries.advanced_search(search_term, search_type, limit)
        return jsonify({
            'search_term': search_term,
            'search_type': search_type,
            'count': len(movies),
            'movies': movies
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/regex/search')
def regex_search():
    """Regex-based movie title search"""
    pattern = request.args.get('pattern', '')
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    if not pattern:
        return jsonify({'error': 'Regex pattern is required'}), 400
    
    try:
        movies = queries.regex_title_search(pattern, limit, offset)
        return jsonify({
            'pattern': pattern,
            'count': len(movies),
            'offset': offset,
            'has_more': len(movies) == limit,
            'movies': movies
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/views/<view_name>')
def get_view_data(view_name):
    """Get data from database views"""
    limit = request.args.get('limit', 20, type=int)
    
    try:
        data = queries.get_view_data(view_name, limit)
        return jsonify({
            'view': view_name,
            'count': len(data),
            'data': data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User Movie Lists API Endpoints
@app.route('/api/user/want-to-watch', methods=['GET'])
def get_user_want_to_watch():
    """Get user's want to watch movies from database"""
    try:
        user_session = get_user_session()
        movies = queries.get_want_to_watch_movies(user_session)
        return jsonify({
            'movies': movies,
            'count': len(movies)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/want-to-watch', methods=['POST'])
def add_to_want_to_watch():
    """Add a movie to user's want to watch list"""
    try:
        data = request.json
        tconst = data.get('tconst')
        if not tconst:
            return jsonify({'error': 'Movie ID (tconst) is required'}), 400
        
        user_session = get_user_session()
        success = queries.add_to_want_to_watch(user_session, tconst)
        
        if success:
            return jsonify({'message': 'Movie added to want to watch list'})
        else:
            return jsonify({'message': 'Movie was already in want to watch list'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/want-to-watch', methods=['DELETE'])
def remove_from_want_to_watch():
    """Remove a movie from user's want to watch list"""
    try:
        data = request.json
        tconst = data.get('tconst')
        if not tconst:
            return jsonify({'error': 'Movie ID (tconst) is required'}), 400
        
        user_session = get_user_session()
        success = queries.remove_from_want_to_watch(user_session, tconst)
        
        if success:
            return jsonify({'message': 'Movie removed from want to watch list'})
        else:
            return jsonify({'message': 'Movie was not in want to watch list'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/want-to-watch/clear', methods=['DELETE'])
def clear_want_to_watch():
    """Clear all movies from user's want to watch list"""
    try:
        user_session = get_user_session()
        success = queries.clear_want_to_watch(user_session)
        
        if success:
            return jsonify({'message': 'Want to watch list cleared'})
        else:
            return jsonify({'error': 'Failed to clear want to watch list'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/watched', methods=['GET'])
def get_user_watched():
    """Get user's watched movies from database"""
    try:
        user_session = get_user_session()
        movies = queries.get_watched_movies(user_session)
        return jsonify({
            'movies': movies,
            'count': len(movies)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/watched', methods=['POST'])
def add_to_watched():
    """Add a movie to user's watched list"""
    try:
        data = request.json
        tconst = data.get('tconst')
        if not tconst:
            return jsonify({'error': 'Movie ID (tconst) is required'}), 400
        
        user_session = get_user_session()
        success = queries.add_to_watched(user_session, tconst)
        
        if success:
            return jsonify({'message': 'Movie added to watched list'})
        else:
            return jsonify({'message': 'Movie was already in watched list'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/watched', methods=['DELETE'])
def remove_from_watched():
    """Remove a movie from user's watched list"""
    try:
        data = request.json
        tconst = data.get('tconst')
        if not tconst:
            return jsonify({'error': 'Movie ID (tconst) is required'}), 400
        
        user_session = get_user_session()
        success = queries.remove_from_watched(user_session, tconst)
        
        if success:
            return jsonify({'message': 'Movie removed from watched list'})
        else:
            return jsonify({'message': 'Movie was not in watched list'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/watched/clear', methods=['DELETE'])
def clear_watched():
    """Clear all movies from user's watched list"""
    try:
        user_session = get_user_session()
        success = queries.clear_watched(user_session)
        
        if success:
            return jsonify({'message': 'Watched list cleared'})
        else:
            return jsonify({'error': 'Failed to clear watched list'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/lists/summary', methods=['GET'])
def get_user_lists_summary():
    """Get summary of user's movie lists"""
    try:
        user_session = get_user_session()
        summary = queries.get_user_movie_lists_summary(user_session)
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Check if database exists
    if not os.path.exists('imdb.db'):
        print("Database not found! Please run 'python database_setup.py' first.")
        exit(1)
    
    print("Starting IMDb Movies Server...")
    print("Open http://localhost:8081 in your browser to explore the API")
    app.run(debug=True, host='0.0.0.0', port=8081) 