from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GameViewSet, RatingViewSet, ReviewViewSet, DownloadViewSet, UserViewSet
from .stats_views import user_genre_stats
from .analytics_views import analytics_data

router = DefaultRouter()
router.register(r'games', GameViewSet, basename='game')
router.register(r'ratings', RatingViewSet, basename='rating')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'downloads', DownloadViewSet, basename='download')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('user-stats/', user_genre_stats, name='user-stats'),
    path('analytics/', analytics_data, name='analytics-data'),
]



