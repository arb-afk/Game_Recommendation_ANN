from rest_framework import viewsets, status, serializers as drf_serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Q, Case, When
from .models import Game, Rating, Review, Download
from .serializers import (
    GameSerializer, RatingSerializer, ReviewSerializer, 
    DownloadSerializer, UserSerializer
)
from .recommender_engine import get_recommender_engine


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    
    def get_queryset(self):
        queryset = Game.objects.all()
        
        # Filter by genre
        genre = self.request.query_params.get('genre', None)
        if genre:
            queryset = queryset.filter(genres__icontains=genre)
            
        # Search by title or description
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
            
        return queryset

    def list(self, request, *args, **kwargs):
        """Override list to add error handling"""
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {'error': str(e), 'detail': 'An error occurred while fetching games. Check server logs for details.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        """Get detailed information about a game including ratings, reviews, and downloads."""
        game = self.get_object()
        serializer = self.get_serializer(game)
        
        # Get user_id from query params
        user_id = request.query_params.get('user_id', None)
        user_rating = None
        user_rating_id = None
        has_downloaded = False
        
        if user_id:
            try:
                user_id = int(user_id)
                try:
                    user = User.objects.get(pk=user_id)
                except User.DoesNotExist:
                    # Auto-create user if not found
                    user = User.objects.create_user(
                        pk=user_id,
                        username=f'user{user_id}',
                        email=f'user{user_id}@example.com'
                    )
                
                # Get user's rating
                try:
                    rating = Rating.objects.get(user=user, game=game)
                    user_rating = rating.rating
                    user_rating_id = rating.id
                except Rating.DoesNotExist:
                    pass
                
                # Check if user has downloaded this game
                has_downloaded = Download.objects.filter(user=user, game=game).exists()
            except (ValueError, Exception) as e:
                pass
        
        # Get recent reviews
        reviews = Review.objects.filter(game=game).order_by('-created_at')[:10]
        reviews_serializer = ReviewSerializer(reviews, many=True)
        
        return Response({
            'game': serializer.data,
            'user_rating': user_rating,
            'user_rating_id': user_rating_id,
            'has_downloaded': has_downloaded,
            'reviews': reviews_serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def recommended(self, request):
        """Get recommended games (sorted by recommendations and ratings)"""
        user_id = request.query_params.get('user_id', None)
        
        games_queryset = None

        # Try ANN recommendations first if user is specified
        if user_id:
            try:
                user_id = int(user_id)
                # Ensure user exists for recommendation logic (though predict_for_user uses ID)
                if not User.objects.filter(pk=user_id).exists():
                    User.objects.create_user(
                        pk=user_id,
                        username=f'user{user_id}',
                        email=f'user{user_id}@example.com'
                    )
                
                engine = get_recommender_engine()
                # Get more candidates to allow for pagination
                recommended_ids = engine.predict_for_user(user_id, top_n=200)
                
                if recommended_ids:
                    # Preserve order of ids
                    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(recommended_ids)])
                    games_queryset = Game.objects.filter(pk__in=recommended_ids).order_by(preserved)
            except Exception as e:
                print(f"ANN recommendation failed: {e}")
                # Fallback to default logic
        
        if games_queryset is None:
            try:
                # "Discovery Mode" Fallback
                # If we don't have ANN recommendations (cold start), don't just show "All Games" (popularity).
                # Instead, show a "Curated Discovery" list: Random high-quality games.
                
                # 1. Filter for high-quality games (Rating >= 4.0)
                # We use a subquery or limit to avoid performance issues with order_by('?')
                high_quality_ids = Game.objects.annotate(
                    avg_rating=Avg('ratings__rating')
                ).filter(
                    avg_rating__gte=4.0
                ).values_list('id', flat=True)[:1000] # Take a pool of top 1000 candidates
                
                # 2. Pick random IDs from this pool
                import random
                high_quality_ids = list(high_quality_ids)
                if len(high_quality_ids) > 50:
                    random_ids = random.sample(high_quality_ids, 50)
                else:
                    random_ids = high_quality_ids
                
                # 3. Fetch these specific games
                games_queryset = Game.objects.filter(pk__in=random_ids)
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                # Fallback to simple ordering if annotations fail
                games_queryset = Game.objects.order_by('-recommendations', '-created_at')

        # Apply Filters
        genre = request.query_params.get('genre', None)
        if genre:
            games_queryset = games_queryset.filter(genres__icontains=genre)
            
        release_year = request.query_params.get('release_year', None)
        if release_year:
            try:
                year = int(release_year)
                games_queryset = games_queryset.filter(release_year=year)
            except ValueError:
                pass
        
        search = request.query_params.get('search', None) # Add search to recommended too for flexibility
        if search:
            games_queryset = games_queryset.filter(
                Q(title__icontains=search) | 
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )

        page = self.paginate_queryset(games_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(games_queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def genres(self, request):
        """Get all unique genres"""
        # This can be slow if done on every request, but for a prototype it's fine.
        # In a real app, you'd have a separate Genre model or a cached list.
        all_genres = set()
        # Only sample from a portion if DB is too large, or use values_list
        genre_strings = Game.objects.exclude(genres='').values_list('genres', flat=True)
        for gs in genre_strings:
            for g in gs.split(';'):
                if g.strip():
                    all_genres.add(g.strip())
        
        return Response(sorted(list(all_genres)))

    @action(detail=False, methods=['get'])
    def my_games(self, request):
        """Get games downloaded by the specified user"""
        user_id = request.query_params.get('user_id', None)
        
        if not user_id:
            return Response({'detail': 'user_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            # Create user if it doesn't exist (for simplicity)
            user = User.objects.create_user(
                username=f'user{user_id}',
                email=f'user{user_id}@example.com'
            )
        
        try:
            # Get base queryset from downloads
            queryset = Game.objects.filter(downloads__user=user)
            
            # Apply filters
            genre = request.query_params.get('genre', None)
            if genre:
                queryset = queryset.filter(genres__icontains=genre)
                
            search = request.query_params.get('search', None)
            if search:
                queryset = queryset.filter(
                    Q(title__icontains=search) | 
                    Q(name__icontains=search) | 
                    Q(description__icontains=search)
                )

            # Paginate
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {'error': str(e), 'detail': 'Failed to fetch user games. Check server logs for details.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response({'detail': 'Rating already exists'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
             return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        # Get user_id from request data
        user_id = self.request.data.get('user')
        if user_id:
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                # Auto-create user if not found (simulating a simple auth system)
                user = User.objects.create_user(
                    pk=user_id,
                    username=f'user{user_id}',
                    email=f'user{user_id}@example.com'
                )
            serializer.save(user=user)
        else:
            raise drf_serializers.ValidationError({'user': 'user field is required'})
    
    def perform_update(self, serializer):
         # Ensure we don't accidentally lose the user or validation doesn't fail
         serializer.save()

    def get_queryset(self):
        queryset = Rating.objects.all()
        user_id = self.request.query_params.get('user_id', None)
        game_id = self.request.query_params.get('game_id', None)
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if game_id:
            queryset = queryset.filter(game_id=game_id)
        
        return queryset


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    
    def perform_create(self, serializer):
        # Get user_id from request data
        user_id = self.request.data.get('user')
        if user_id:
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                # Auto-create user if not found
                user = User.objects.create_user(
                    pk=user_id,
                    username=f'user{user_id}',
                    email=f'user{user_id}@example.com'
                )
            serializer.save(user=user)
        else:
            raise drf_serializers.ValidationError({'user': 'user field is required'})
    
    def get_queryset(self):
        queryset = Review.objects.all()
        game_id = self.request.query_params.get('game_id', None)
        
        if game_id:
            queryset = queryset.filter(game_id=game_id)
        
        return queryset


from django.db import IntegrityError

class DownloadViewSet(viewsets.ModelViewSet):
    queryset = Download.objects.all()
    serializer_class = DownloadSerializer
    
    def create(self, request, *args, **kwargs):
        """Override create to handle duplicates gracefully"""
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            # If download already exists, return 200 OK
            return Response({'status': 'already_downloaded'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        # Get user_id from request data
        user_id = self.request.data.get('user')
        if user_id:
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                # Auto-create user if not found
                user = User.objects.create_user(
                    pk=user_id,
                    username=f'user{user_id}',
                    email=f'user{user_id}@example.com'
                )
            
            # Check if download already exists to avoid IntegrityError here if possible
            # (though unique constraint race conditions can still happen, caught in create)
            if Download.objects.filter(user=user, game=serializer.validated_data['game']).exists():
                # Raise IntegrityError to be caught by create()
                raise IntegrityError("Download already exists")
                
            serializer.save(user=user)
        else:
            raise drf_serializers.ValidationError({'user': 'user field is required'})
    
    def get_queryset(self):
        queryset = Download.objects.all()
        user_id = self.request.query_params.get('user_id', None)
        game_id = self.request.query_params.get('game_id', None)
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if game_id:
            queryset = queryset.filter(game_id=game_id)
        
        return queryset


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

