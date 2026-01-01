# Game Recommender System

A web application for rating, downloading, and reviewing games, built with Django REST Framework backend and Vue.js frontend. This system includes an artificial neural network recommender system trained on user interaction data.

## Features

- **Recommended Games**: AI-driven recommendations based on user ratings and downloads.
- **Browse All Games**: Explore the full catalog with search and genre filtering.
- **My Games**: Track your downloads and personal library.
- **Game Details**: View average ratings, download counts, and recent reviews.
- **Interactive UI**: Rate games (1-5 stars), download/remove games, and leave reviews.

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework, TensorFlow (Keras)
- **Frontend**: Vue.js 3, Vite, Axios
- **ML/Data**: Pandas, NumPy, Scikit-learn

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js & npm

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. (Optional) Populate data and train the model:
```bash
# Import games from CSV
python manage.py import_csv_data

# Optional: Populate with sample/random data for testing
python manage.py restore_downloads
python manage.py randomize_ratings

# Train the recommender engine
python manage.py train_recommender
```

6. Start the development server:
```bash
python manage.py runserver
```

The backend API will be available at `http://127.0.0.1:8000`

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

The frontend will be available at `http://localhost:5173`

## Management Commands

The backend includes several management commands for data maintenance:

- `import_csv_data`: Imports games from `a_steam_data_2021_2025.csv`.
- `train_recommender`: Trains the collaborative filtering model using current ratings and downloads.
- `restore_downloads`: Restores initial download counts from the CSV recommendations field.
- `randomize_ratings`: Generates random rating data for testing the recommendation engine.
- `randomize_downloads`: Generates random download data.
- `populate_sample_data`: Adds a small set of sample data for quick testing.
- `check_setup`: Verifies that the environment and database are correctly configured.

## Usage

1. Start both the Django backend and Vue.js frontend servers.
2. Open `http://localhost:5173` in your browser.
3. Enter a User ID in the navigation bar to simulate different users.
4. Interact with games (rate, download, review) to generate data.
5. Periodically run `python manage.py train_recommender` to update the recommendation model based on new interactions.

## Database Models

- **Game**: Stores game metadata (appid, name, genres, categories, price, etc.).
- **Rating**: User-provided star ratings (1-5).
- **Review**: User-written feedback.
- **Download**: Tracks user ownership of games.
- **User**: Django's built-in user model (simulated via User ID in this prototype).

## Notes

- The system uses SQLite by default.
- CORS is configured for development.
- The recommender model is saved in `backend/games/ml_models/`.

