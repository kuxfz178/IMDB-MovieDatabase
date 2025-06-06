# IMDb Movies Database Web App

A Flask web application that serves IMDb movie data with search functionality, personalized recommendations, and a user-friendly dashboard.

## Project Files

- `database_setup.py` - Creates SQLite database and loads movie data from TSV files
- `imdb_queries.py` - Database query functions and recommendation engine  
- `app.py` - Flask web server with API endpoints and web interface
- `requirements.txt` - Python package dependencies
- `imdb.db` - SQLite database file (created after setup)
- `data/title.basics.tsv` - IMDb movie dataset (required)

## Data Files

Due to GitHub's file size limits, the large data files are not included in this repository. You have two options:

### Option 1: Download Fresh from IMDb (Recommended)
Run the automatic download script:
```bash
python download_data.py
```

### Option 2: Manual Download
Download manually from IMDb:
1. Visit the [IMDb Non-Commercial Datasets](https://developer.imdb.com/non-commercial-datasets/) documentation
2. Go to [IMDb Datasets](https://datasets.imdbws.com/) for direct downloads
3. Download `title.basics.tsv.gz` 
4. Extract to `data/title.basics.tsv`

**Important:** This project uses IMDb's non-commercial datasets. Please ensure you comply with [IMDb's terms and conditions](https://developer.imdb.com/non-commercial-datasets/) for personal and non-commercial use.

**Note:** The database file (`imdb.db`) will be created automatically when you run the setup script.

## Setup from Source

### Prerequisites
- Python 3.8+
- IMDb `title.basics.tsv` file placed in `data/` directory
- At least 1GB free disk space

### 1. Create Virtual Environment
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Database
```bash
python database_setup.py
```
This will:
- Create SQLite database with movie schema
- Load and filter movie data (movies only, ~716K records)
- Create performance indexes
- Takes approximately 10-15 minutes

Expected output:
```
Setting up IMDb Movies database...
Tables created successfully!
Loading movie data...
Processed 100000 rows, found 72053 movies so far...
Database setup complete!
Movies loaded: 716,482
```

## Running the Web App

### Start the Server
```bash
python app.py
```

The server starts on `http://localhost:8081`

## How to Interact

### 1. API Documentation Page
Visit `http://localhost:8081` to see:
- Database statistics
- Available API endpoints
- Interactive testing buttons

### 2. Interactive Dashboard  
Visit `http://localhost:8081/dashboard` for:
- **Movie Search**: Search by title or browse by genre
- **Want to Watch List**: Click ❤️ to add movies to your watchlist (stored in database)
- **Already Watched**: Track movies you've seen with 👁️ button (stored in database)
- **Personalized Recommendations**: Get suggestions based on your want to watch list
- **Infinite Scroll**: Load more movies with "Load More" button
- **Current Movies Only**: Filters out movies released after 2025
- **Persistent Storage**: Your movie lists are saved in the database and persist across sessions

### 3. API Endpoints
- `GET /api/movies/search?q=batman&limit=20&offset=0` - Search movies with pagination
- `GET /api/movies/genre/Action?limit=20&offset=0` - Filter by genre with pagination
- `GET /api/movies/year/2023` - Movies by year
- `GET /api/stats` - Database statistics
- `POST /api/recommendations` - Get personalized recommendations
- `GET /api/regex/search?pattern=^The.*&limit=20&offset=0` - Regex pattern search
- `GET /api/search/advanced?q=Action+Comedy&type=genre_pattern` - Advanced search
- `GET /api/views/recent_quality_movies` - Database views

#### User Movie Lists API
- `GET /api/user/want-to-watch` - Get user's want to watch movies
- `POST /api/user/want-to-watch` - Add movie to want to watch list
- `DELETE /api/user/want-to-watch` - Remove movie from want to watch list
- `DELETE /api/user/want-to-watch/clear` - Clear entire want to watch list
- `GET /api/user/watched` - Get user's watched movies
- `POST /api/user/watched` - Add movie to watched list
- `DELETE /api/user/watched` - Remove movie from watched list
- `DELETE /api/user/watched/clear` - Clear entire watched list
- `GET /api/user/lists/summary` - Get summary of user's movie lists

**Note**: All search endpoints support `limit` (default 20) and `offset` (default 0) parameters for pagination.

## Usage Examples

### Search for Movies
1. Go to `/dashboard`
2. Type movie name in search box
3. Click "Search" or press Enter

### Get Recommendations
1. Search and add movies to your want to watch list (click ❤️ buttons)
2. Mark movies as watched (click 👁️ buttons)  
3. Once you have at least 5 total interactions (want to watch + watched), click "Generate Recommendations"
4. System analyzes your preferences and suggests similar movies

### Track Your Viewing
- **Want to Watch**: Click ❤️ to add movies to your watchlist
- **Mark as Watched**: Click 📺 to track movies you've already seen
- **Visual Indicators**: Movies show different colors (green for want to watch, blue for watched, purple for both)
- **Easy Management**: Clear all lists or remove individual items

### Advanced Search Features
- **Regex Search**: Click "Regex Search" for pattern matching (e.g., `^The.*man$`)
- **Genre Patterns**: Use `Action+Comedy` (both) or `Action|Comedy` (either)
- **Year Patterns**: Use `199*` for 1990s movies

### View Statistics
- Visit main page for database overview
- Check `/api/stats` for detailed statistics

## Troubleshooting

**Database not found error**: Run `python database_setup.py` first

**Port 8081 in use**: Change port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=9000)
```

**No movies found**: Verify `data/title.basics.tsv` file exists and is properly formatted

## Database Schema

**movies** table:
- `tconst` - IMDb identifier (Primary Key)
- `primaryTitle` - Movie title  
- `startYear` - Release year
- `runtimeMinutes` - Duration
- `genres` - Comma-separated genres
- `isAdult` - Content rating (0/1)

**want_to_watch** table:
- `id` - Auto-incrementing ID (Primary Key)
- `user_session` - User session identifier
- `tconst` - Movie ID (Foreign Key to movies.tconst)
- `added_date` - When movie was added to list

**watched_movies** table:
- `id` - Auto-incrementing ID (Primary Key)
- `user_session` - User session identifier
- `tconst` - Movie ID (Foreign Key to movies.tconst)
- `watched_date` - When movie was marked as watched

## System Requirements

- **Storage**: ~200MB for database, ~1GB for TSV processing
- **Memory**: ~500MB during setup, ~50MB during operation  
- **Setup Time**: 10-15 minutes for database initialization
- **Performance**: <200ms for most queries