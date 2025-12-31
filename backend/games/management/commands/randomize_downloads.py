from django.core.management.base import BaseCommand
from games.models import Game
import random
from django.db import transaction

class Command(BaseCommand):
    help = 'Randomize download counts (recommendations field) for all games to simulate real usage data'

    def handle(self, *args, **options):
        self.stdout.write('Randomizing download counts for games...')
        
        games = Game.objects.all()
        count = games.count()
        
        if count == 0:
            self.stdout.write(self.style.WARNING('No games found. Please import data first.'))
            return

        batch_size = 1000
        updated_count = 0

        # We will use a weighted distribution to simulate real world scenarios
        # where a few games have massive downloads and many have fewer.
        
        with transaction.atomic():
            for game in games:
                # 5% of games are "hits" (100k - 5M downloads)
                # 15% are "popular" (10k - 100k downloads)
                # 30% are "moderate" (1k - 10k downloads)
                # 50% are "niche" (0 - 1k downloads)
                
                rand_val = random.random()
                
                if rand_val < 0.05:
                    downloads = random.randint(100000, 5000000)
                elif rand_val < 0.20:
                    downloads = random.randint(10000, 100000)
                elif rand_val < 0.50:
                    downloads = random.randint(1000, 10000)
                else:
                    downloads = random.randint(0, 1000)
                
                game.recommendations = downloads
                game.save()
                
                updated_count += 1
                if updated_count % 1000 == 0:
                     self.stdout.write(f'Updated {updated_count}/{count} games...')

        self.stdout.write(self.style.SUCCESS(f'Successfully randomized downloads for {updated_count} games!'))
