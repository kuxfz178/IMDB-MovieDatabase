from flask import Flask, jsonify, request, render_template, session
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

@app.route('/')
def index():
    """Main page with API documentation"""
    return render_template('index.html')

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
    return render_template('dashboard.html')

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