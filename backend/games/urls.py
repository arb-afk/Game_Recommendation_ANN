from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GameViewSet, RatingViewSet, ReviewViewSet, DownloadViewSet, UserViewSet

router = DefaultRouter()
router.register(r'games', GameViewSet, basename='game')
router.register(r'ratings', RatingViewSet, basename='rating')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'downloads', DownloadViewSet, basename='download')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]



