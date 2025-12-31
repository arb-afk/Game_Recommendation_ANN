from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from games.models import Game, Rating
import random
from django.db import transaction

class Command(BaseCommand):
    help = 'Generate random ratings for all games to ensure average rating is displayed everywhere'

    def handle(self, *args, **options):
        self.stdout.write('Generating synthetic ratings for all games...')
        
        # 1. Ensure we have a pool of "Reviewer" users
        reviewers = []
        user_password = 'password123'
        
        self.stdout.write('Ensuring reviewer users exist...')
        with transaction.atomic():
            for i in range(1, 51):  # Create 50 reviewers
                username = f'reviewer_{i}'
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': f'{username}@example.com',
                        'first_name': 'Reviewer',
                        'last_name': str(i)
                    }
                )
                if created:
                    user.set_password(user_password)
                    user.save()
                reviewers.append(user)
        
        # 2. Get all games
        # We only need IDs to be efficient
        game_ids = list(Game.objects.values_list('id', flat=True))
        total_games = len(game_ids)
        
        if total_games == 0:
            self.stdout.write(self.style.WARNING('No games found. Please import data first.'))
            return

        self.stdout.write(f'Found {total_games} games. Generating ratings...')

        # 3. Generate Ratings
        # We will check which games already have ratings to avoid duplicates/errors if run multiple times
        # But for speed, we'll just try to ignore conflicts or use bulk_create with ignore_conflicts (Django 4.1+)
        # Since we are on Django 4.2+, we can use ignore_conflicts=True.
        
        ratings_to_create = []
        batch_size = 5000
        processed_count = 0
        
        for game_id in game_ids:
            # Decide how many ratings this game gets: 1 to 4
            # We want most games to have at least 1 rating.
            num_ratings = random.choices([1, 2, 3, 4], weights=[40, 30, 20, 10], k=1)[0]
            
            # Pick random reviewers
            game_reviewers = random.sample(reviewers, num_ratings)
            
            for reviewer in game_reviewers:
                # Weighted rating: Skew towards 3, 4, 5
                # 1: 5%, 2: 10%, 3: 20%, 4: 35%, 5: 30%
                rating_val = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30], k=1)[0]
                
                ratings_to_create.append(Rating(
                    user=reviewer,
                    game_id=game_id,
                    rating=rating_val
                ))
            
            processed_count += 1
            
            if len(ratings_to_create) >= batch_size:
                Rating.objects.bulk_create(ratings_to_create, ignore_conflicts=True)
                self.stdout.write(f'Processed {processed_count}/{total_games} games... ({len(ratings_to_create)} ratings added)')
                ratings_to_create = []

        # Flush remaining
        if ratings_to_create:
            Rating.objects.bulk_create(ratings_to_create, ignore_conflicts=True)
            self.stdout.write(f'Processed {processed_count}/{total_games} games... ({len(ratings_to_create)} ratings added)')

        self.stdout.write(self.style.SUCCESS(f'Successfully generated ratings for all games!'))
