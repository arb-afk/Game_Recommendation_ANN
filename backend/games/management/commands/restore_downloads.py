import csv
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from games.models import Game

class Command(BaseCommand):
    help = 'Restore download counts (recommendations) from the original CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-file',
            type=str,
            default='a_steam_data_2021_2025.csv',
            help='Path to CSV file (relative to project root)'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        
        # Locate CSV file
        from django.conf import settings
        base_dir = Path(settings.BASE_DIR) if hasattr(Path, '__class__') else Path(str(settings.BASE_DIR))
        project_root = base_dir.parent
        csv_path = project_root / csv_file
        
        if not os.path.exists(csv_path):
             # Try current directory
             csv_path = Path(csv_file)
             if not csv_path.exists():
                self.stdout.write(self.style.ERROR(f'CSV file not found at {csv_path} or project root.'))
                return

        self.stdout.write(f'Restoring recommendation counts from {csv_path}...')
        
        updated_count = 0
        skipped_count = 0
        
        # Read CSV and update database
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Pre-fetch all games to minimize DB queries
                # storing as {appid: game_object}
                self.stdout.write('Loading games from database...')
                games_dict = {game.appid: game for game in Game.objects.all()}
                self.stdout.write(f'Loaded {len(games_dict)} games.')
                
                updates = []
                
                for row in reader:
                    try:
                        appid = int(row['appid'])
                        if appid in games_dict:
                            rec_val = 0
                            if row.get('recommendations'):
                                try:
                                    rec_val = int(row['recommendations'])
                                except (ValueError, TypeError):
                                    pass
                            
                            game = games_dict[appid]
                            if game.recommendations != rec_val:
                                game.recommendations = rec_val
                                updates.append(game)
                        else:
                            skipped_count += 1
                            
                    except ValueError:
                        continue
                
                # Bulk update
                if updates:
                    self.stdout.write(f'Updating {len(updates)} games...')
                    # We process in batches to avoid memory issues
                    batch_size = 5000
                    for i in range(0, len(updates), batch_size):
                        batch = updates[i:i + batch_size]
                        Game.objects.bulk_update(batch, ['recommendations'])
                        self.stdout.write(f'  Updated batch {i} - {i + len(batch)}')
                        
                    updated_count = len(updates)
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading CSV: {e}'))
            return

        self.stdout.write(self.style.SUCCESS(
            f'Successfully restored downloads from CSV!\n'
            f'  Updated: {updated_count} games\n'
            f'  Skipped (not in DB): {skipped_count}'
        ))
