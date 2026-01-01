# How to Run Locally

## Prerequisites
- Python 3.10+
- Node.js & npm

## 1. Backend Setup (Terminal 1)

Navigate to the backend directory:
```bash
cd backend
```

Install the required Python packages:
```bash
pip install -r requirements.txt
```

Initialize the database:
```bash
python manage.py migrate
```

**(Optional) Populate Data:**
If this is your first time running it or your database is empty, run these commands in order:
```bash
python manage.py import_csv_data
python manage.py restore_downloads
python manage.py randomize_ratings
python manage.py train_recommender
```

Start the server:
```bash
python manage.py runserver
```
The API is now running at `http://127.0.0.1:8000`.

## 2. Frontend Setup (Terminal 2)

Open a new terminal and navigate to the frontend directory:
```bash
cd frontend
```

Install the required Node packages:
```bash
npm install
```

Start the development server:
```bash
npm run dev
```

## 3. Use the App
Open your browser and visit the URL shown in the frontend terminal (usually `http://localhost:5173`).
