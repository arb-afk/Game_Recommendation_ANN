import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from django.conf import settings
from .models import Rating, Game, Download
from django.contrib.auth.models import User
import pickle
from sklearn.preprocessing import MultiLabelBinarizer

class RecommenderEngine:
    def __init__(self):
        self.model_path = os.path.join(settings.BASE_DIR, 'games', 'ml_models', 'recommender_model.keras')
        self.encoders_path = os.path.join(settings.BASE_DIR, 'games', 'ml_models', 'encoders.pkl')
        self.user2user_encoded = {}
        self.user_encoded2user = {}
        self.game2game_encoded = {}
        self.game_encoded2game = {}
        self.mlb = None # MultiLabelBinarizer for genres
        self.game_popularity = {} # Store log(popularity) for games
        self.model = None
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        self.load_model()

    def load_model(self):
        """Load the trained model and encoders if they exist."""
        if os.path.exists(self.model_path) and os.path.exists(self.encoders_path):
            try:
                self.model = keras.models.load_model(self.model_path)
                with open(self.encoders_path, 'rb') as f:
                    encoders = pickle.load(f)
                    self.user2user_encoded = encoders['user2user_encoded']
                    self.user_encoded2user = encoders['user_encoded2user']
                    self.game2game_encoded = encoders['game2game_encoded']
                    self.game_encoded2game = encoders['game_encoded2game']
                    self.mlb = encoders.get('mlb')
                    self.game_popularity = encoders.get('game_popularity', {})
                print("Model and encoders loaded successfully.")
            except Exception as e:
                print(f"Error loading model: {e}")
                self.model = None

    def train(self):
        """Train the Hybrid Recommendation Model (User CF + Content Based)."""
        print("Fetching data for training...")
        
        # 1. Fetch Interactions
        ratings = list(Rating.objects.all().values('user_id', 'game_id', 'rating'))
        downloads = list(Download.objects.all().values('user_id', 'game_id'))
        
        # Combine data
        data = []
        seen = set()
        
        for r in ratings:
            data.append({'user_id': r['user_id'], 'game_id': r['game_id'], 'rating': r['rating']})
            seen.add((r['user_id'], r['game_id']))
            
        for d in downloads:
            if (d['user_id'], d['game_id']) not in seen:
                data.append({'user_id': d['user_id'], 'game_id': d['game_id'], 'rating': 4.5})
                
        if len(data) < 10:
            print("Not enough data to train model (need at least 10 interactions).")
            return False

        df = pd.DataFrame(data)
        
        # 2. Prepare Encoders
        user_ids = df["user_id"].unique().tolist()
        self.user2user_encoded = {x: i for i, x in enumerate(user_ids)}
        self.user_encoded2user = {i: x for i, x in enumerate(user_ids)}
        
        game_ids = df["game_id"].unique().tolist()
        self.game2game_encoded = {x: i for i, x in enumerate(game_ids)}
        self.game_encoded2game = {i: x for i, x in enumerate(game_ids)}
        
        # 3. Fetch Game Metadata (Genres AND Popularity)
        print(f"Fetching metadata for {len(game_ids)} unique games...")
        game_genres = {}
        self.game_popularity = {} # Reset
        
        # Fetch all games efficiently
        # Use simple .values() to avoid object creation overhead and huge SQL IN clause
        all_games_data = Game.objects.all().values('id', 'genres', 'recommendations')
        
        game_ids_set = set(game_ids)
        
        for g_data in all_games_data:
            gid = g_data['id']
            if gid in game_ids_set:
                # Genre
                raw_genres = g_data['genres']
                genres_list = [genre.strip() for genre in raw_genres.split(';')] if raw_genres else []
                game_genres[gid] = genres_list
                
                # Popularity (Log Transformation)
                # Log1p(x) = log(1 + x) handles 0s and compresses large range
                recs = g_data['recommendations'] if g_data['recommendations'] else 0
                self.game_popularity[gid] = np.log1p(recs)
            
        # 4. Multi-hot Encode Genres
        self.mlb = MultiLabelBinarizer()
        all_genres_list = list(game_genres.values())
        self.mlb.fit(all_genres_list)
        num_genres = len(self.mlb.classes_)
        
        # 5. Prepare Training Vectors
        df["user"] = df["user_id"].map(self.user2user_encoded)
        df["game"] = df["game_id"].map(self.game2game_encoded)
        
        # Normalize ratings
        min_rating = 1.0
        max_rating = 5.0
        df["rating"] = df["rating"].apply(lambda x: (x - min_rating) / (max_rating - min_rating))
        
        # Inputs
        user_input_data = df["user"].values
        game_input_data = df["game"].values
        
        # Genre input
        genre_input_list = [game_genres[gid] for gid in df["game_id"].values]
        genre_input_data = self.mlb.transform(genre_input_list)
        
        # Popularity input
        popularity_input_data = np.array([self.game_popularity.get(gid, 0.0) for gid in df["game_id"].values])
        
        y = df["rating"].values
        
        # 6. Build Hybrid Model
        num_users = len(self.user2user_encoded)
        num_games = len(self.game2game_encoded)
        embedding_size = 50
        
        # --- Input Layers ---
        user_input = layers.Input(shape=(1,), name="user_input")
        game_input = layers.Input(shape=(1,), name="game_input")
        genre_input = layers.Input(shape=(num_genres,), name="genre_input")
        popularity_input = layers.Input(shape=(1,), name="popularity_input") # Single float value
        
        # --- Embeddings ---
        user_embedding = layers.Embedding(num_users, embedding_size, name="user_embedding")(user_input)
        user_vec = layers.Flatten()(user_embedding)
        
        game_embedding = layers.Embedding(num_games, embedding_size, name="game_embedding")(game_input)
        game_vec = layers.Flatten()(game_embedding)
        
        # --- Interaction ---
        prod = layers.Dot(axes=1, name="dot_product")([user_vec, game_vec])
        
        # --- Feature Processing ---
        genre_dense = layers.Dense(32, activation="relu", name="genre_dense")(genre_input)
        
        # --- Concatenation ---
        # Add popularity to the mix
        concat = layers.Concatenate()([user_vec, game_vec, prod, genre_dense, popularity_input])
        
        # Deep Layers
        dense1 = layers.Dense(64, activation='relu')(concat)
        dropout1 = layers.Dropout(0.2)(dense1)
        dense2 = layers.Dense(32, activation='relu')(dropout1)
        
        output = layers.Dense(1, activation='sigmoid')(dense2)
        
        self.model = keras.Model(inputs=[user_input, game_input, genre_input, popularity_input], outputs=output)
        self.model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001), loss='binary_crossentropy')
        
        print(f"Training Hybrid Model on {len(df)} samples...")
        self.model.fit(
            x=[user_input_data, game_input_data, genre_input_data, popularity_input_data],
            y=y,
            batch_size=64,
            epochs=15,
            verbose=1,
            validation_split=0.1
        )
        
        print("Saving model...")
        self.model.save(self.model_path)
        with open(self.encoders_path, 'wb') as f:
            pickle.dump({
                'user2user_encoded': self.user2user_encoded,
                'user_encoded2user': self.user_encoded2user,
                'game2game_encoded': self.game2game_encoded,
                'game_encoded2game': self.game_encoded2game,
                'mlb': self.mlb,
                'game_popularity': self.game_popularity
            }, f)
            
        print("Training complete.")
        return True

    def predict_for_user(self, user_id, top_n=20):
        """Predict top N games for a user."""
        if self.model is None or self.mlb is None:
            return []
            
        if user_id not in self.user2user_encoded:
            return []
            
        encoded_user_id = self.user2user_encoded[user_id]
        
        # Identify candidate games
        rated_games = Rating.objects.filter(user_id=user_id).values_list('game_id', flat=True)
        downloaded_games = Download.objects.filter(user_id=user_id).values_list('game_id', flat=True)
        interacted_games = set(rated_games) | set(downloaded_games)
        
        known_game_ids = list(self.game2game_encoded.keys())
        candidate_ids = [gid for gid in known_game_ids if gid not in interacted_games]
        
        if not candidate_ids:
            return []
            
        # Prepare inputs
        user_input = np.array([encoded_user_id] * len(candidate_ids))
        game_input = np.array([self.game2game_encoded[gid] for gid in candidate_ids])
        
        # Optimizing prediction fetch
        # Fetch genres and popularity for candidates efficiently
        # Since we have self.game_popularity in memory from load_model/train, use it
        # But we still need genres.
        
        # Optimization: Fetch genres only if we don't have them in memory.
        # But for now, let's just fetch them to be safe as self.game_popularity doesn't store genres
        # A better production system would cache {id -> features} entirely.
        
        # We'll re-fetch just for candidates to ensure correctness
        # Use .values() again for speed
        # Optimization: Fetch ALL games to avoid SQLite "too many SQL variables" error
        # caused by passing 65k+ IDs to id__in
        all_games_data = Game.objects.all().values('id', 'genres', 'recommendations')
        
        cand_map = {d['id']: d for d in all_games_data if d['id'] in set(candidate_ids)}
        
        genre_lists = []
        popularity_vals = []
        
        for gid in candidate_ids:
            if gid in cand_map:
                d = cand_map[gid]
                # Genre
                raw = d['genres']
                g_list = [g.strip() for g in raw.split(';')] if raw else []
                genre_lists.append(g_list)
                
                # Popularity - prefer the trained value if available to match scale, 
                # otherwise compute fresh log1p
                if gid in self.game_popularity:
                    pop = self.game_popularity[gid]
                else:
                    recs = d['recommendations'] if d['recommendations'] else 0
                    pop = np.log1p(recs)
                popularity_vals.append(pop)
            else:
                genre_lists.append([])
                popularity_vals.append(0.0)
                
        genre_input = self.mlb.transform(genre_lists)
        popularity_input = np.array(popularity_vals)
        
        # Predict
        predictions = self.model.predict(
            [user_input, game_input, genre_input, popularity_input], 
            verbose=0
        ).flatten()
        
        top_indices = predictions.argsort()[-top_n:][::-1]
        
        recommended_ids = [candidate_ids[i] for i in top_indices]
        return recommended_ids

# Global instance
_engine_instance = None

def get_recommender_engine():
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = RecommenderEngine()
    return _engine_instance
