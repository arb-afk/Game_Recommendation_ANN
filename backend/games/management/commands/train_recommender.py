from django.core.management.base import BaseCommand
from games.recommender_engine import RecommenderEngine

class Command(BaseCommand):
    help = 'Trains the Neural Network recommendation model'

    def handle(self, *args, **options):
        self.stdout.write('Starting model training...')
        engine = RecommenderEngine()
        success = engine.train()
        
        if success:
            self.stdout.write(self.style.SUCCESS('Successfully trained recommendation model'))
        else:
            self.stdout.write(self.style.WARNING('Training failed or not enough data'))
