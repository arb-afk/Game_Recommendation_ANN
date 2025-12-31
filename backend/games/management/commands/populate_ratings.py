from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from games.models import Game, Rating, Download
import random
from django.db import transaction

class Command(BaseCommand):
    help = 'Populate database with synthetic ratings based on genre preferences (requires Games to be imported first)'

    def handle(self, *args, **options):
        # 1. Check for Games
        game_count = Game.objects.count()
        if game_count == 0:
            self.stdout.write(self.style.ERROR('No games found! Please run "python manage.py import_csv_data" first.'))
            return

        self.stdout.write(f'Found {game_count} games. Generating synthetic user data...')

        # 2. Define Genres (based on Steam data observation)
        all_genres = set()
        # Sample genres from first 1000 games to build a list
        for g in Game.objects.all()[:1000]:
            if g.genres:
                for genre in g.genres.split(';'):
                    all_genres.add(genre.strip())
        
        all_genres = list(all_genres)
        if not all_genres:
            all_genres = ['Action', 'Adventure', 'RPG', 'Strategy', 'Indie', 'Casual', 'Simulation']
        
        self.stdout.write(f'Identified {len(all_genres)} genres.')

        # 3. Create Users with Preferences
        users_to_create = 20
        created_users = []
        
        with transaction.atomic():
            for i in range(1, users_to_create + 1):
                username = f'gamer_{i}'
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': f'{username}@example.com',
                        'first_name': f'Gamer',
                        'last_name': str(i)
                    }
                )
                if created:
                    user.set_password('pass1234')
                    user.save()
                
                # Assign 2-3 favorite genres
                fav_genres = random.sample(all_genres, k=random.randint(2, 4))
                created_users.append({'user': user, 'fav_genres': fav_genres})
                self.stdout.write(f'User {username} likes: {", ".join(fav_genres)}')

            # 4. Generate Ratings
            ratings_created = 0
            downloads_created = 0
            
            # Pre-fetch games to avoid N+1 queries (fetching a subset for efficiency if DB is huge)
            # For 20k games, fetching all IDs and Genres is fine.
            all_games = list(Game.objects.values('id', 'genres'))
            
            for user_data in created_users:
                user = user_data['user']
                fav = user_data['fav_genres']
                
                # User rates 50-100 games
                num_ratings = random.randint(50, 100)
                
                # Pick random games
                games_to_rate = random.sample(all_games, k=num_ratings)
                
                for game in games_to_rate:
                    game_id = game['id']
                    game_genres = game['genres'].split(';') if game['genres'] else []
                    game_genres = [g.strip() for g in game_genres]
                    
                    # Logic: If game has a genre the user likes, high rating. Else, random (mostly lower).
                    # Check intersection
                    matches = any(g in fav for g in game_genres)
                    
                    if matches:
                        # 80% chance of high rating (4-5), 20% chance of meh (3)
                        if random.random() < 0.8:
                            rating_val = random.choice([4, 5])
                        else:
                            rating_val = 3
                    else:
                        # 80% chance of low rating (1-2-3), 20% chance of surprise like (4)
                        if random.random() < 0.8:
                            rating_val = random.choice([1, 2, 3])
                        else:
                            rating_val = 4
                    
                    Rating.objects.update_or_create(
                        user=user,
                        game_id=game_id,
                        defaults={'rating': rating_val}
                    )
                    ratings_created += 1
                    
                    # If rating is 5, add a download
                    if rating_val == 5:
                        Download.objects.get_or_create(user=user, game_id=game_id)
                        downloads_created += 1

        self.stdout.write(self.style.SUCCESS(f'Done! Created {ratings_created} ratings and {downloads_created} downloads.'))
