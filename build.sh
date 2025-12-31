#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Convert static files
python backend/manage.py collectstatic --no-input

# Apply migrations
python backend/manage.py migrate

# IMPORTANT for Render Free:
# 1. Do NOT run 'train_recommender' here. It will crash the 512MB RAM instance.
# 2. The trained model files (ml_models/*.keras, *.pkl) MUST be committed to Git.
# 3. Running 'import_csv_data' for 65k rows might time out. 
#    If it fails, run it locally and use a hosted DB like Neon.tech or Supabase.
