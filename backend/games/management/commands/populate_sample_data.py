from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from games.models import Game, Rating, Review, Download
import random
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Populate database with sample games, users, ratings, reviews, and downloads'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create sample users
        users = []
        for i in range(1, 11):
            user, created = User.objects.get_or_create(
                username=f'user{i}',
                defaults={
                    'email': f'user{i}@example.com',
                    'first_name': f'User{i}',
                    'last_name': 'Test'
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
            users.append(user)
            self.stdout.write(f'Created user: {user.username}')
        
        # Create sample games
        game_titles = [
            'Epic Adventure Quest', 'Space Explorer 3000', 'Racing Legends',
            'Puzzle Master Pro', 'Fantasy Kingdom', 'Cyberpunk Arena',
            'Mystery Mansion', 'Sports Championship', 'Strategy Empire',
            'Action Hero', 'RPG Chronicles', 'Simulation City',
            'Platform Jump', 'Shooting Stars', 'Battle Royale',
            'Card Collector', 'Word Wizard', 'Music Maker',
            'Dance Revolution', 'Fitness Trainer'
        ]
        
        genres = ['Action', 'Adventure', 'RPG', 'Strategy', 'Puzzle', 'Sports', 'Racing', 'Simulation']
        developers = ['GameStudio A', 'GameStudio B', 'Indie Dev', 'Big Games Inc', 'Creative Studios']
        
        games = []
        for i, title in enumerate(game_titles, start=1000000): # Start appids from 1,000,000
            game, created = Game.objects.get_or_create(
                appid=i,
                defaults={
                    'title': title,
                    'description': f'An exciting game called {title}. Experience amazing gameplay, stunning graphics, and engaging storylines. Perfect for gamers of all ages!',
                    'genres': random.choice(genres),
                    'developer': random.choice(developers),
                    'release_date': str(datetime.now().date() - timedelta(days=random.randint(0, 1000)))
                }
            )
            games.append(game)
            if created:
                self.stdout.write(f'Created game: {game.title}')
        
        # Create ratings
        self.stdout.write('Creating ratings...')
        for game in games:
            # Each game gets ratings from random users
            num_ratings = random.randint(5, len(users))
            rating_users = random.sample(users, num_ratings)
            
            for user in rating_users:
                Rating.objects.get_or_create(
                    user=user,
                    game=game,
                    defaults={
                        'rating': random.randint(1, 5)
                    }
                )
        
        # Create downloads
        self.stdout.write('Creating downloads...')
        for user in users:
            # Each user downloads 3-8 random games
            num_downloads = random.randint(3, min(8, len(games)))
            downloaded_games = random.sample(games, num_downloads)
            
            for game in downloaded_games:
                Download.objects.get_or_create(
                    user=user,
                    game=game
                )
        
        # Create reviews
        self.stdout.write('Creating reviews...')
        review_templates = [
            'Great game! Really enjoyed playing it.',
            'Amazing graphics and gameplay. Highly recommend!',
            'Fun game but could use some improvements.',
            'One of the best games I\'ve played this year.',
            'Decent game, worth trying out.',
            'Not my cup of tea, but others might enjoy it.',
            'Excellent game design and mechanics.',
            'Good value for money. Lots of content.',
            'Could be better, but still enjoyable.',
            'Absolutely love this game! 10/10 would play again.'
        ]
        
        for game in games:
            # Each game gets 2-5 reviews
            num_reviews = random.randint(2, min(5, len(users)))
            review_users = random.sample(users, num_reviews)
            
            for user in review_users:
                Review.objects.get_or_create(
                    user=user,
                    game=game,
                    defaults={
                        'content': random.choice(review_templates)
                    }
                )
        
        self.stdout.write(self.style.SUCCESS('Successfully populated sample data!'))
        self.stdout.write(f'Created {len(users)} users, {len(games)} games')



