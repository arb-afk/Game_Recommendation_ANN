from django.core.management.base import BaseCommand
from django.db import connection
from games.models import Game


class Command(BaseCommand):
    help = 'Check if database is set up correctly'

    def handle(self, *args, **options):
        self.stdout.write('Checking database setup...\n')
        
        # Check if tables exist
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
            self.stdout.write(f'Found {len(tables)} tables in database')
            
            if 'games_game' in tables:
                self.stdout.write(self.style.SUCCESS('✓ games_game table exists'))
            else:
                self.stdout.write(self.style.ERROR('✗ games_game table does NOT exist'))
                self.stdout.write('  Run: python manage.py migrate')
                return
            
            # Check game count
            try:
                count = Game.objects.count()
                self.stdout.write(f'\nGames in database: {count}')
                if count == 0:
                    self.stdout.write(self.style.WARNING('⚠ No games found in database'))
                    self.stdout.write('  Run: python manage.py import_csv_data')
                else:
                    self.stdout.write(self.style.SUCCESS(f'✓ Found {count} games'))
                    
                # Check a sample game
                if count > 0:
                    game = Game.objects.first()
                    self.stdout.write(f'\nSample game: {game.title} (appid: {game.appid})')
                    self.stdout.write(f'  Genres: {game.genres}')
                    self.stdout.write(f'  Recommendations: {game.recommendations}')
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error accessing games: {e}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Database error: {e}'))
            self.stdout.write('  Make sure migrations are run: python manage.py migrate')

