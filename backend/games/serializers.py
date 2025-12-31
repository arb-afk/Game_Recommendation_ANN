from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Game, Rating, Review, Download


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class GameSerializer(serializers.ModelSerializer):
    average_rating = serializers.ReadOnlyField()
    total_downloads = serializers.ReadOnlyField()
    total_reviews = serializers.ReadOnlyField()
    genre_list = serializers.ReadOnlyField()
    category_list = serializers.ReadOnlyField()
    primary_genre = serializers.ReadOnlyField()
    
    class Meta:
        model = Game
        fields = ['id', 'appid', 'title', 'name', 'description', 'release_year', 
                  'release_date', 'genres', 'genre_list', 'primary_genre', 'categories', 
                  'category_list', 'price', 'recommendations', 'developer', 'publisher',
                  'average_rating', 'total_downloads', 'total_reviews', 
                  'created_at', 'updated_at']


class RatingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Rating
        fields = ['id', 'user', 'game', 'rating', 'created_at', 'updated_at']
        # Remove default validators to prevent issues with read-only 'user' field
        # during updates. We handle uniqueness via explicit checks or DB constraints.
        validators = []

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['game'] = GameSerializer(instance.game).data
        return response


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'game', 'content', 'created_at', 'updated_at']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['game'] = GameSerializer(instance.game).data
        return response


class DownloadSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Download
        fields = ['id', 'user', 'game', 'downloaded_at']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['game'] = GameSerializer(instance.game).data
        return response

