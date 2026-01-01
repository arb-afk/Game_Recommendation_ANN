from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Rating, Game
from django.db.models import Count
from collections import defaultdict

@api_view(['GET'])
def user_genre_stats(request):
    user_id = request.query_params.get('user_id')
    if not user_id:
        return Response([])

    # Get games rated highly (>3) by user
    user_ratings = Rating.objects.filter(user_id=user_id, rating__gt=3).values_list('game__genres', flat=True)
    
    if not user_ratings:
        return Response({'labels': [], 'data': []})

    genre_counts = defaultdict(int)
    for raw_genres in user_ratings:
        if raw_genres:
            genres = [g.strip() for g in raw_genres.split(';')]
            for g in genres:
                genre_counts[g] += 1
    
    # Sort and take top 10
    sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:8]
    
    data = {
        'labels': [k for k, v in sorted_genres],
        'datasets': [{
            'label': 'Your Taste Profile',
            'backgroundColor': 'rgba(66, 184, 131, 0.2)',
            'borderColor': '#42b883',
            'pointBackgroundColor': '#42b883',
            'data': [v for k, v in sorted_genres]
        }]
    }
    
    return Response(data)
