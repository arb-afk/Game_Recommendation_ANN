import csv
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from games.models import Game
from datetime import datetime


class Command(BaseCommand):
    help = 'Import games from CSV file (a_steam_data_2021_2025.csv)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-file',
            type=str,
            default='a_steam_data_2021_2025.csv',
            help='Path to CSV file (relative to project root)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of games to import (for testing)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing games before importing'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        limit = options['limit']
        clear = options['clear']
        
        # Get the project root directory using Django's BASE_DIR
        # BASE_DIR points to backend/, so project root is one level up
        from django.conf import settings
        base_dir = Path(settings.BASE_DIR) if hasattr(Path, '__class__') else Path(str(settings.BASE_DIR))
        project_root = base_dir.parent  # Go up one level from backend/ to project root
        csv_path = project_root / csv_file
        
        # Convert to string for compatibility
        csv_path = str(csv_path)
        
        # If not found, try a few alternative locations
        if not os.path.exists(csv_path):
            alternatives = [
                os.path.join(str(project_root), csv_file),  # Project root
                os.path.join(str(base_dir), csv_file),      # Backend directory
                csv_file,                                    # Current directory
            ]
            for alt_path in alternatives:
                if os.path.exists(alt_path):
                    csv_path = os.path.abspath(alt_path)
                    break
        
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'\nCSV file not found: {csv_file}'))
            self.stdout.write(f'\nTried the following locations:')
            self.stdout.write(f'  1. {csv_path}')
            try:
                from django.conf import settings
                base_dir = Path(settings.BASE_DIR) if isinstance(settings.BASE_DIR, Path) else Path(str(settings.BASE_DIR))
                project_root = base_dir.parent
                self.stdout.write(f'  2. {str(project_root / csv_file)}')
                self.stdout.write(f'  3. {str(base_dir / csv_file)}')
                self.stdout.write(f'  4. {os.path.join(os.getcwd(), csv_file)}')
                self.stdout.write(f'\nTip: The CSV file should be at: {str(project_root / csv_file)}')
            except Exception as e:
                self.stdout.write(f'  (Could not determine alternative paths: {e})')
            self.stdout.write(f'\nPlease ensure the CSV file "{csv_file}" exists in the project root directory.')
            self.stdout.write(f'Current working directory: {os.getcwd()}')
            return
        
        if clear:
            self.stdout.write('Clearing existing games...')
            Game.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing games'))
        
        self.stdout.write(f'Importing games from {csv_path}...')
        
        imported = 0
        skipped = 0
        errors = 0
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                with transaction.atomic():
                    for row_num, row in enumerate(reader, start=2):
                        if limit and imported >= limit:
                            break
                        
                        try:
                            # Parse appid
                            appid = int(row['appid'])
                            
                            # Check if game already exists
                            if Game.objects.filter(appid=appid).exists():
                                skipped += 1
                                continue
                            
                            # Parse name/title
                            name = row.get('name', '').strip()
                            title = name  # Use name as title
                            
                            # Parse release_year
                            release_year = None
                            if row.get('release_year'):
                                try:
                                    release_year = int(row['release_year'])
                                except (ValueError, TypeError):
                                    pass
                            
                            # Parse release_date (keep as string)
                            release_date = row.get('release_date', '').strip()
                            
                            # Parse genres and categories
                            genres = row.get('genres', '').strip()
                            categories = row.get('categories', '').strip()
                            
                            # Parse price
                            price = None
                            if row.get('price'):
                                try:
                                    price = float(row['price'])
                                except (ValueError, TypeError):
                                    pass
                            
                            # Parse recommendations
                            recommendations = 0
                            if row.get('recommendations'):
                                try:
                                    recommendations = int(row['recommendations'])
                                except (ValueError, TypeError):
                                    pass
                            
                            # Parse developer and publisher
                            developer = row.get('developer', '').strip()
                            publisher = row.get('publisher', '').strip()
                            
                            # Create game
                            game = Game.objects.create(
                                appid=appid,
                                title=title,
                                name=name,
                                release_year=release_year,
                                release_date=release_date,
                                genres=genres,
                                categories=categories,
                                price=price,
                                recommendations=recommendations,
                                developer=developer,
                                publisher=publisher,
                                description=f"{title} - {genres}"  # Basic description
                            )
                            
                            imported += 1
                            
                            if imported % 1000 == 0:
                                self.stdout.write(f'Imported {imported} games...')
                        
                        except Exception as e:
                            errors += 1
                            if errors <= 10:  # Only show first 10 errors
                                self.stdout.write(
                                    self.style.WARNING(f'Error on row {row_num}: {str(e)}')
                                )
                            continue
                
                self.stdout.write(self.style.SUCCESS(
                    f'\nImport completed!\n'
                    f'  Imported: {imported} games\n'
                    f'  Skipped (duplicates): {skipped} games\n'
                    f'  Errors: {errors} rows'
                ))
        
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'CSV file not found: {csv_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading CSV file: {str(e)}'))

