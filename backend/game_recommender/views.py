from django.http import JsonResponse

def api_root(request):
    """Simple root view that provides API information"""
    return JsonResponse({
        'message': 'Game Recommender API',
        'version': '1.0',
        'endpoints': {
            'games': '/api/games/',
            'recommended_games': '/api/games/recommended/',
            'my_games': '/api/games/my_games/?user_id=<user_id>',
            'ratings': '/api/ratings/',
            'reviews': '/api/reviews/',
            'downloads': '/api/downloads/',
            'users': '/api/users/',
            'admin': '/admin/',
        },
        'frontend': 'http://localhost:8080',
        'documentation': 'See README.md for full API documentation'
    })



