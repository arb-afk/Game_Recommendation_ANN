# Game Recommender System

A web application for rating, downloading, and reviewing games, built with Django REST Framework backend and Vue.js frontend. This system is designed to collect user interaction data for training an artificial neural network recommender system.

## Features

- **Recommended Games Page**: Displays top-rated games based on ratings and downloads
- **All Games Page**: Browse all available games with search and genre filtering
- **My Games Page**: View games downloaded by the current user
- **Game Details Modal**: View detailed information including:
  - Average rating
  - Total downloads count
  - Total reviews count
  - User's personal rating (if logged in)
  - Download/Remove download functionality
  - Recent reviews

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework
- **Frontend**: Vue.js 3, Vue Router, Axios
- **Build Tool**: Vite

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r ../requirements.txt
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser (optional, for admin access):
```bash
python manage.py createsuperuser
```

6. Import games from CSV file:
```bash
python manage.py import_csv_data
```
This will import all games from `a_steam_data_2021_2025.csv` in the project root.

Options:
- `--limit N`: Import only first N games (for testing)
- `--clear`: Clear existing games before importing

7. Start the Django development server:
```bash
python manage.py runserver
```

The backend API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:8080`

## API Endpoints

- `GET /api/games/` - List all games
- `GET /api/games/recommended/` - Get recommended games
- `GET /api/games/my_games/` - Get user's downloaded games
- `GET /api/games/{id}/details/` - Get detailed game information
- `POST /api/ratings/` - Create a rating
- `PUT /api/ratings/{id}/` - Update a rating
- `POST /api/downloads/` - Record a game download
- `GET /api/reviews/?game_id={id}` - Get reviews for a game
- `POST /api/reviews/` - Create a review

## Usage

1. Start both the Django backend and Vue.js frontend servers
2. Open `http://localhost:8080` in your browser
3. Enter a User ID in the navigation bar (you can use any integer, or create users through Django admin)
4. Browse games, rate them, download them, and leave reviews
5. The data collected will be stored in the SQLite database and can be used for training your ANN recommender system

## Database Models

- **Game**: Stores game information from CSV (appid, name, title, release_year, release_date, genres, categories, price, recommendations, developer, publisher)
- **Rating**: User ratings for games (1-5 stars)
- **Review**: User-written reviews for games
- **Download**: Tracks which users have downloaded which games
- **User**: Django's built-in user model

The Game model is based on the Steam data CSV structure with fields:
- `appid`: Unique Steam App ID
- `name`/`title`: Game name
- `release_year`/`release_date`: Release information
- `genres`: Semicolon-separated list of genres
- `categories`: Semicolon-separated list of categories
- `price`: Game price
- `recommendations`: Number of recommendations (used as initial download count)
- `developer`/`publisher`: Developer and publisher information

## Notes

- The system uses SQLite by default for development
- CORS is configured to allow requests from the Vue.js frontend
- User authentication is simplified for this use case - you can use any user ID
- For production, you should implement proper authentication and use a more robust database

## Future Enhancements

- Implement the actual neural network recommender system
- Add user authentication and registration
- Add more sophisticated recommendation algorithms
- Add game images and media
- Implement pagination for large game lists
- Add filtering and sorting options

